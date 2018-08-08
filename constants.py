import os

#replace the code below with the pathway to the infections folder and desired values
OLD_DIR= r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
NEW_DIR = os.path.join(OLD_DIR, 'infections_new')
FIRST_ONTOLOGY = 'DOID-NCBITaxon.csv'
SECOND_ONTOLOGY = 'DOID-HP.csv'
THIRD_ONTOLOGY = 'human_pathogens.csv'
NLTK_DIR = 'NLTKTestBatch'
ABSTRACT_DATA = 'pmabstracts.csv'
UNIQUE_ONTOLOGY = 'unique_full_ontology_plus_symptoms.csv'
BATCH_PATH = 'batch'
ALL_BATCH = 'allbatch'
NEW_NLTK_DIR = 'newNLTKTestBatch'
TAGGED_BATCH = 'taggedbatch'
COMBINED_CSV = 'combined.csv'
FULL_ONTOLOGY = 'full_ontology.csv'
TRAINING_SET = 'ner_trainingset.csv'
TESTING_SET = 'ner_dataset.csv'
CLEAN_TEXT = 'cleantext'
NAME_DIS_BATCH = 'namedisbatch'
DIS_SYMP_BATCH = 'dissympbatch'
NAME_SYMP_BATCH = 'namesympbatch'
