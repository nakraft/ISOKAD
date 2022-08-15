'''
Using unsupervised learning (SVMs/Isolation Forests), identify anomalys present. Through construction of 
Knowledge Graphs, relationship traits are hypothesized to be easily seperable to support classification. 
Main.py will load data, generate entity types, build the feature set and run the associated models. 

INPUT: choice of dataset. 
OUTPUT: processed dataset with features and model decisions. 

Contributions: 
- All work in this package has been adopted from Asara Senaratne (https://github.com/AsaraSenaratne/anomaly-detection-kg). 
Code has been improved for speed/efficiency and additions have been made to increase the accuracy of the model and feature set. 
- The main addition to this work has included: comparison of modelling techniques with labelled synthetic fraud data, 
introducing customization of anomalous material and expansion of modelling technique to include Isolation Forests. 
'''

import argparse
import time
import numpy as np

import anomaly_support
import load_data
import feature_building
import model_training
import entity_recognition

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='Anomaly Detection', 
                        description='You are looking to detect anomalies in knowledge graphs.')
    parser.add_argument("-a", '--all', action = "store_true",  
                        help='How much of the anomaly process are you interested in running? \
                                Installation through modelling, or uniquely modelling.')
    parser.add_argument("-d", dest='dataset', type=str, default='YAGO', 
                        help='Choose which dataset you are interested in evaluating.')
    parser.add_argument("-entity", dest='entity', type=str, default='spacy', 
                        help='How do you want to recognize these entities?')
    parser.add_argument("-o", '--override', action = "store_true",  
                        help='Do you want to override the current feature set and rerun.')
    parser.add_argument("-c", '--custom', action = "store_true",  
                        help='Do you want to customize the features based off a known anomalous area of interest? Custom targets can be set in anomaly_support. ')
    
    args = parser.parse_args()

    dataset_options = {
        # first variable points to dataset to load, second shows if this data has evaluation ground truth. 
        'YAGO' : (load_data.get_yago, False), # includes full dataset processed with SPACY
        'YAGO-b' : (load_data.get_yago, False), # includes full dataset processed with SPACY, non-defined entities processed by SAS
        'YAGO-sas' : (load_data.get_yago, False), # includes full dataset processed with SAS 
        'YAGO-sample' : (load_data.get_yago, False), # sample dataset for testing purposes (1000 entries, or .1% of the data)
        'fraud' : (load_data.get_fraud, True) # fraud data for use in comparison. No NER needed as there is a defined ontology. 
    }
    anomaly_support.set_data(args.dataset)

    if args.all: 
        # run installation guide and load data if you are interested in the full procedure of modelling 
        import installation
        
        data_start = time.time()
        dataset_options[args.dataset][0](100)
        print("---------------------")
        print("All data has been loaded.")
        print("---------------------")
        data_end = time.time()
        
        if args.dataset == 'YAGO' and args.entity == 'spacy' : 
            entity_start = time.time()
            entity_recognition.spacy_recognize()
            entity_end = time.time()

    # once data is loaded and system installed, build the features 
    feature_start = time.time()
    feature_building.main(args.override, args.custom)
    feature_end = time.time()

    # train the model 
    svm_time, forest_time = model_training.forest(dataset_options[args.dataset][1], args.custom)

    print("---------------------")
    print("Model Training and Evaluation Complete.")
    print("---------------------")
    # visualize and export anomalous results and EDA

    print("Here is your performance report:")
    if args.all: 
        print("Data Load Time: " + str(data_end - data_start))
        if args.dataset == 'YAGO' and args.entity == 'spacy': 
            print("Entity Recognition Time: " + str(entity_end - entity_start))
    print("Feature Building Time: " + str(feature_end - feature_start))
    print("SVM Model Training, Predictions and Evaluation: " + str(svm_time))
    print("Isolation Forest Model Training, Predictions and Evaluation: " + str(forest_time))

