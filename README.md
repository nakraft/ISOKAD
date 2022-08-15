# ISOKAD
## Isolation Forests for Knowledge Graph Anomaly Detection
This project is a part of the [Laboratory for Analytic Sciences](https://ncsu-las.org) at NC State University and aims at developing a method for unsupervised detection of anomalous behavior in knowledge graphs. 

## Project Intro

The amount of data pouring into the hands of analysts daily is overwhelming. To support the exploration of this data and reduce the manual labor required for triage, ISOKAD is under development to produce a method identifying anomlous behavior in knowledge graphs. The following requirements were identified as nessecary to support our ideal use case: 

- Build a method to identify anomalies, which categorizes the severity of the anomaly and is domain agnostic 
- Ensure methods are unsupervised 
- Provide a way for hypothesis checking through injecting foresight of anticipated anomalies into modelling

## Getting Started

1. Clone this repo (for help see this [tutorial](https://help.github.com/articles/cloning-a-repository/)).
2. Establish a virtual enviornment using Python 3.7 Instantiate with the needed [requirements](requirements.txt).
```
python -m venv anomaly_venv
source anomaly_venv/bin/activate 

pip install -r requirements.txt
```

When the virtual enviornment is done being used, deactive it using ```deactivate```. The enviornment must be running to utilize the anomaly detection model. 

3. Data: 

This method has been utilized with two main datasets:   

  a. YAGO (Yet Another Great Ontology) is scraped from Wikipedia data and consists of general knowledge in a KG format. There is no labelled ground truth for anomalous nodes; in this dataset anomalous nodes would include contradictions, inaccurate facts, or sparse data.    
  - [More information on YAGO](https://yago-knowledge.org/data/yago1/yago-1.0.0-turtle.7z) can be found here; the dataset will be automatically downloaded through running the code base.    
  - After the program downloads the data, it needs to perform entity recognition to categorize each node into types (ie. Organization, Person, Place, etc). This has been precomputed on [Spacy](https://github.com/nakraft/ISOKAD/blob/main/assets/yago_entities.csv) and [SAS](https://github.com/nakraft/ISOKAD/blob/main/assets/yago_entities_sas.csv) NER algorithms. 

  b. PAYSIM is a synthetic fraud dataset with fraudulent transactions labelled as a ground truth. Download the entity pairs directly from the sandbox or the associated google drive link. Place the downloaded file in the **assets** folder. 
  - The original PAYSIM data can be found in a [Neo4J Sandbox](https://neo4j.com/sandbox/) by selecting **Fraud Detection**. For use in ISOKAD, the node-relationship-node entity pairs were extracted. 
```
# the command to pull relationships from Neo4J
MATCH (a)-[r]-(b)
RETURN a, LABELS(a), TYPE(r), b, LABELS(b)
# In testing, use a limit. When downloading the full data - which is nessecary to ensure that a comprehensive state of the world is being considered in the model - you will need to download in batches or increae the timeout duration in settings. 
LIMIT 10 
```
- The fraud data can be found [here](https://github.com/nakraft/ISOKAD/blob/main/assets/fraud.csv). **Note: entities were already labelled so no NER is needed)**
      
4. Run the Model. 

  The model can be run through the **main.py** file. All steps previously completed will be skipped to ensure fast processing. For example, once the data is loaded, entities are computed and the features are generated, you can rerun the model with different parameters - still through the **main.py** file - without having to recompute the previous steps. Here are the basic arguments for **main.py**.  
  
  - -d : Choose which dataset you would like to run on. YAGO or fraud. If you are testing on other datasets, see below on how to include new datasets in the files. 
  - -o : Use if you would like to override previous computing of features or data, this will override any files and recompute. This is a good option to use if you are experimenting with new features. 
  - -c : Use to include custom features in modelling efforts. Other wise only the base features will be utilized. 
  - -a : Use if you would like to run through the whole process, or proceed directly to modelling. 
  - -entity : Enter -entity to specify which NER algorithm to use, Spacy is the default. This is irrelevant if NER is not needed. 

  **Note: currently the only model being run from main is Isolation Forests. SVM modelling is functioning, but takes 30+ hours to compute on 1 million entity pairs. If you choose to use SVM modelling, run just the model_training.py file with the argumen to run the SVM model.**
  
 5. Results will be generated and logged within the results directory. 
 
 ## Data Flexibility 
 
 Any knowledge graph representation of a dataset can be used within ISOKAD. For best results, datasets that meet the closed world assumption will perform better. The following 5 fields are needed for processing: node A identifier, node A type, relationship type, node B identifier, node B type. 
 
 To test these results on other datasets, update the following areas: 
 
 - The dictionaries of data types within main.py, load_data.py, and anomaly_support.py need to be updated to include a common key for the data being used.
  - main.py : The tuple value for the key should consist of the function name to process the data (define within the load_data.py file) and a True/False value for if NER is needed to identify entities. 
  - load_data.py : The function name to load the data properly into the assets folder. Create this custom function name above to process data. 
  - anomaly_support.py : The tuple value for the key should consist of the relative pathways for the (entity pairs, entity types, results). 
 
 ## Moving Forward
 
 Additional work could be done to apply ISOKAD to temporal knowledge graphs. The fraud dataset includes timestamps and features could be developed to see how facts change over time based on the relative frequency of a particular entity pair types in one time block over another, or the 'newness' of entity types that are developing over time. 
 
 In addition, more features could be generated for hypothesis testing through anomaly detection mechanisms. Both of these new features would be an extention of the work ongoing in [custom_features.py](https://github.com/nakraft/ISOKAD/blob/main/sources/custom_features.py). 
 
 ## Neo4J
 
 More information on ISOKADs work within Neo4J can be found within our [Neo4J guide](https://github.com/nakraft/ISOKAD/blob/main/neo4j.md). 

