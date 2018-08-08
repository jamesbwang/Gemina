import os

#replace the code below with the pathway to the infections folder
OLD_DIR= r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
NEW_DIR = os.path.join(OLD_DIR, 'infections_new')
FIRST_ONTOLOGY = 'DOID-NCBITaxon.csv'
SECOND_ONTOLOGY = 'DOID-HP.csv'
THIRD_ONTOLOGY = 'human_pathogens.csv'
NLTKDIR = 'NLTKTestBatch'
ABSTRACT_DATA = 'pmabstracts.csv'
UNIQUE_ONTOLOGY = 'unique_full_ontology_plus_symptoms.csv'
