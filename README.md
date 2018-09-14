Install Instructions:

Virtualenv install
Redis install for server session
Make sure redis is running

Install JRE for synthea generator
Make sure config has the right path to synthea script
Update synthea properties in /synthea/src/main/resources/synthea.properties
--> exporter.baseDirectory = projectroot/seed/fhir/patients
--> exporter.years_of_history = 0
--> exporter.fhir.export = true
--> exporter.fhir.use_shr_extensions = false
--> generate.append_numbers_to_person_names = false


Change output / settings for Synthea
Shoudl put FHIR resources in right directory



Run deploy tasks