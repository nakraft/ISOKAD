
# data store for YAGO data 

triples_yago = "../assets/yago_relations.csv"
yago_nodes = "../assets/yago_nodes.csv"
yago_node_labels = "../assets/yago_node_labels.csv"
yago_entities = "../assets/yago_entities.csv"
yago_results = "../results/yago_results1.csv"

triples_yago_sas = "../assets/yago_relations_sas.csv"
yago_nodes_sas = "../assets/yago_nodes.csv"
yago_node_labels_sas = "../assets/yago_node_labels.csv"
yago_entities_sas = "../assets/yago_entities_sas.csv"
yago_results_sas = "../results/yago_results_sas1.csv"

triples_yago_b = "../assets/yago_relations_b.csv"
yago_nodes_b = "../assets/yago_nodes.csv"
yago_node_labels_b = "../assets/yago_node_labels.csv"
yago_entities_b = "../assets/yago_entities_b.csv"
yago_results_b = "../results/yago_results_b1.csv"

triples_yago_sample = "../assets/yago_relations_sample.csv"
yago_results_sample = "../results/yago_results_sample1.csv"

# begin data store for fraud data 

raw_fraud = "../assets/fraud.csv"

triples_fraud = "../assets/fraud_relations.csv"
fraud_nodes = "../assets/fraud_nodes.csv"
fraud_entities = "../assets/fraud_entities.csv" 
fraud_results = "../results/fraud_results1.csv"

ground_truth = "properties.fraud"

def set_data(dataset_name): 

    to_features = {
        'YAGO' : (triples_yago, yago_entities, yago_results),
        'YAGO-b' : (triples_yago_b, yago_entities_b, yago_results_b), 
        'YAGO-sas' : (triples_yago_sas, yago_entities_sas, yago_results_sas), 
        'YAGO-sample' : (triples_yago_sample, yago_entities, yago_results_sample), # can use entities as this is the proper subset of information, switch to use other dictionary to get another entity mapping
        'fraud' : (triples_fraud, fraud_entities, fraud_results), 
        'timeFraud' : (time_features, timefraud_entities, time_results)
    }

    global model_data, model_entity, model_features, model_results
    model_data = to_features[dataset_name][0]
    model_features = to_features[dataset_name][0].split(".csv")[0] + "_features.csv"
    model_entity = to_features[dataset_name][1]
    model_results = to_features[dataset_name][2]

    global target
    global initial_attribute_count
    if 'YAGO' in dataset_name: 
        initial_attribute_count = 18
        # target = 'http://yago-knowledge.org/resource/wikicategory_Politics_of_the_Republic_of_Macedonia'
        target = 'http://yago-knowledge.org/resource/Democratic_Party_(United_States)'
        target_entity = 'LOCATION'
    else:
        initial_attribute_count = 19
        target = 13100
        target_entity = 'Client'
    

