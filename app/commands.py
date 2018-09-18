import os, subprocess, sys, time, click, unittest
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.main.utils.demographics import random_demographics
from app.main.utils.synthea import run_synthea
from app.main.models.source_data import SourceData
from app.fhir.models.codesets import process_fhir_codeset, get_fhir_codeset
from app.fhir.models.patient import Patient
from app.user.models.user import User
from app.user.models.role import Role
from app.user.models.app_permission import AppPermission
from app.user.models.app_group import AppGroup


@click.command()
@with_appcontext
def test():
    """
    Run the unit tests.
    """
    os.environ['FLASK_CONFIG'] = 'testing'
    current_app.config['TESTING'] = True
    current_app.config['FLASK_DEBUG'] = True
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@click.command()
@with_appcontext
def deploy():
    """Command line utility to complete deployment tasks:
     1) Drop all tables (optional)
     2) Upgrade to latest Alembic revision (optional)
     3) Create new tables if introduced in revision
     4) Initialize app permisions, user roles and admin user
     5) Create random users (optional) """
    if click.confirm(text='Are you sure you want to proceed?', default=False, show_default=True):
        if click.confirm('Upgrade to latest Alembic revision?', default=True, show_default=True):
            print()
            print("Upgrading to Alembic head revision if needed...")
            from flask_migrate import upgrade
            upgrade()
            print("Alembic revision up to date!")
            print()
        if click.confirm(text='Do you want to update CodeSystems and ValueSets?', default=False):
            config = current_app.config
            valuesets = config.get('VALUESET_IMPORT')
            codesystems = config.get('CODESYSTEM_IMPORT')

            items = [codesystems, valuesets]

            sd_to_process = []
            if items:
                for code_dict in items:
                    if isinstance(code_dict, dict):
                        for key in code_dict:
                            print('Requesting codeset from url: {}'.format(code_dict.get(key)))
                            sd = get_fhir_codeset(url=code_dict.get(key))
                            if sd:
                                sd_to_process.append(sd)
            if sd_to_process:
                print("Codesets were retrieved and are now being processed.")
                for sd in sd_to_process:
                    if isinstance(sd, SourceData):
                        process_fhir_codeset(source_data=sd)
                print("{} codesets were imported and processed!".format(len(sd_to_process) + 1))
            else:
                print("All codesets were already up to date or they could not retrieved online.")

        print()
        print("Initializing app permissions...")
        AppPermission.initialize_app_permissions()
        print("Initializing user roles...")
        Role.initialize_roles()
        print("Creating default App Groups")
        AppGroup.initialize_app_groups()
        print("Creating admin user...")
        User.initialize_admin_user()
        print()

        if click.confirm('Create randomly generated users?', default=True, show_default=True):
            user_create_number = click.prompt(text="How many random users do you want to create?: ", default=99,
                                              type=int)
            if not user_create_number:
                user_create_number = 10
            print("Creating " + str(user_create_number) + " random user(s)...")
            user_list = []
            print("Generating a library of random demographics to use...")
            demo_list = random_demographics(number=int(user_create_number))
            print("Creating user objects...")
            print(user_create_number, end="...")
            while len(user_list) < int(user_create_number):
                user = User()
                user.randomize_user(demo_dict=demo_list.pop(0))
                user_list.append(user)
                print("{}".format(int(user_create_number) - len(user_list)), end='...', flush=True)
            print()
            print("Persisting objects to the database...")
            db.session.add_all(user_list)
            db.session.commit()
            total_users = str(len(user_list))
            print()
            print("Total random users created: " + total_users)

        print("Process completed without errors.")
    else:
        print("Oh thank god............")
        print("That was a close call!")


@click.command()
@with_appcontext
def drop_all():
    """Drop all tables in the database"""
    if click.confirm(text='This will drop all tables, do you want to continue?', default=False, show_default=True):
        db.engine.execute("drop schema if exists public cascade")
        db.engine.execute("create schema public")
        print("All tables have been dropped.")


@click.command()
@with_appcontext
def gunicorn():
    """Starts the application with the Gunicorn
    webserver on the localhost bound to port 5000"""

    ret = subprocess.call(
        ['gunicorn', '--bind', '0.0.0.0:5000', 'unkani:app'])
    sys.exit(ret)


@click.command()
@with_appcontext
def patients():
    """Create randomly generated patients"""
    if click.confirm('Create randomly generated patients?', default=True, show_default=True):
        patient_create_number = click.prompt(text="How many random patients do you want to create?: ", default=100,
                                             type=int)
        remaining = int(patient_create_number)
        print("Creating " + str(patient_create_number) + " random patient(s)...")
        t1 = time.clock()
        demo_list = random_demographics(number=remaining)
        for demo in demo_list:
            Patient.create_random_patient(demo_dict=demo)
        db.session.commit()
        t2 = time.clock()
        print("{} total patients created in {} seconds".format(patient_create_number, str(round(t2 - t1, 3))))
        print("Patient create time was {} seconds".format(round((t2 - t1) / patient_create_number, 3)))


@click.command()
@click.option('--population', '-p', default=100, type=int)
def synthea(population):
    """Create synthetic patient records using Synthea"""
    run_synthea(total_population=population)
