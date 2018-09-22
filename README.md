#Unkani-Server
Bootstrap for healthcare data platforms

##Install Instructions:
1. Clone git repo
2. Install server dependencies
..* Postgresql@9.6
..* Redis
3. Install and configure Synthea & Java Runtime Engine
    Install JRE for synthea generator
    Make sure config has the right path to synthea script
    Update synthea properties in `/synthea/src/main/resources/synthea.properties`
    ```
    --> exporter.baseDirectory = projectroot/seed/fhir/patients
    --> exporter.years_of_history = 0
    --> exporter.fhir.export = true
    --> exporter.fhir.use_shr_extensions = false
    --> generate.append_numbers_to_person_names = false
    ```

4. Run Redis / Postgresql in daemon mode
5. Create virtualenv from python 3.6.X
6. `pip install -r requirements.txt`
7. Review and confirm environment variables
8. Run webserver

#Features:

##Password Hashing
Unkani uses the bcrypt password hashing function, based on the blowfish block cipher to generate
a cryptographic hash.  The hash is salted, adding additional entropy to the function.  Bcrypt is
an expensive key setup function which is resistant to brute-force and rainbow table attacks. 
See the [flask-bcrypt extension](https://flask-bcrypt.readthedocs.io/en/latest/) for more details.

##Synthetic Patient Generation
Unkani uses [Synthea](https://synthetichealth.github.io/synthea/), an open-source synthetic 
patient generator that models the medical history of synthetic patients.  The Synthea java module 
is used to generate FHIR documents representing full patient history. Each patient's history is 
simulated from birth to their current age and is subjected to vetted clinical modules representing
common disease progression and treatment scenarios.  The models are informed by NIH and CDC statistics 
as well as input from real-world clinicians.