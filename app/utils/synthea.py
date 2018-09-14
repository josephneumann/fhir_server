import os
import subprocess
from config import config
from random import randint

config_object = config[os.getenv('FLASK_CONFIG') or 'default']

# Tuple (State, City, Population Weight)
# None for City will use state-wide random cities
synthea_geography = [
    ('Wisconsin', 'Madison', 200)
    , ('Wisconsin', 'Milwaukee', 100)
    , ('Wisconsin', 'Appleton', 100)
    , ('Wisconsin', 'Green Bay', 100)
    , ('Wisconsin', 'Racine', 100)
    , ('Wisconsin', 'Kenosha', 100)
    , ('Wisconsin', None, 100)  # This will use random cities in Wisconsin
    , ('Wisconsin', 'Fitchburg', 25)
    , ('Wisconsin', 'Sun Prairie', 20)
    , ('Wisconsin', 'Middleton', 15)
    , ('Wisconsin', 'Waunakee', 9)
    , ('Wisconsin', 'Verona', 7)
]


def get_total_weight(synthea_settings):
    total_weight = 0
    for x in synthea_settings:
        _, _, add_num = x
        total_weight += int(add_num)
    return total_weight


def run_synthea(total_population, synthea_path=None, synthea_settings=synthea_geography):
    if not synthea_path:
        synthea_path = config_object.SYNTHEA_SCRIPT_LOCATION
    total_weight = get_total_weight(synthea_settings)
    for x in synthea_settings:
        state, city, weight = x
        city_population = round((int(weight) / int(total_weight)) * total_population)
        cmd = [os.path.join(synthea_path, 'run_synthea'), '-p', str(city_population), '-s', str(randint(0, 99999)),
               state]
        if city:
            cmd.append(city)
        subprocess.call(cmd, cwd=synthea_path)
    subprocess.call(['rm', '-r', os.path.join(synthea_path, 'output/cwd')])  # Get rid of cdw files
