import os

#replace the code below with the pathway to the infections folder
dir=r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
newdir = os.path.join(dir, 'infections_new')
firstOntology = 'DOID-NCBITaxon.csv'
secondOntology = 'DOID-HP.csv'
mFile = 'human_pathogens.csv'
NLTKDIR = 'NLTKTestBatch'
ABSTRACT_DATA = 'pmabstracts.csv'
UNIQUE_ONTOLOGY = 'unique_full_ontology_plus_symptoms.csv'
