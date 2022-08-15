import os 
import json
import requests 
import csv
import pandas as pd

import argparse
import py7zr 
from rdflib import Graph,FOAF,URIRef, RDF, Literal, RDFS, plugin
plugin.register('json-ld', 'Serializer', 'rdfextras.serializers.jsonld', 'JsonLDSerializer')

import anomaly_support

# Contribution by Asara, https://github.com/AsaraSenaratne/anomaly-detection-kg
def convert_to_graph(sample_size): 
    print("Converting graph to dataframe - Asara logic")
    with open(anomaly_support.triples_yago, 'w', encoding="utf-8") as yago_links:
        writer = csv.writer(yago_links)
        writer.writerow(["subject", "predicate", "object"])
        for statement in graph:
            if statement[1] == RDF.type or isinstance(statement[2], Literal):
                continue
            else:
                writer.writerow([statement[0], statement[1], statement[2]])

    if sample_size != 100: 
        links = pd.read_csv(anomaly_support.triples_yago)
        links = links.sample((sample_size * len(links) / 100), random_state = 354)
        links.to_csv(anomaly_support.triples_yago, index=False)

    with open(anomaly_support.yago_nodes, 'w', encoding="utf-8") as yago_nodes:
        writer = csv.writer(yago_nodes)
        writer.writerow(["subject", "predicate", "object"])
        for statement in graph:
            if statement[1] == RDF.type:
                writer.writerow([statement[0],"isa", statement[2]])
            elif statement[1]==RDFS.label and isinstance(statement[2], Literal) and RDFS.subClassOf:
                writer.writerow([statement[0],"has_label" , statement[2]])
            elif statement[1]==RDFS.subClassOf and isinstance(statement[2], Literal):
                writer.writerow([statement[0],"subClassOf" , statement[2]])
            elif statement[1]==RDFS.subPropertyOf and isinstance(statement[2], Literal):
                writer.writerow([statement[0],"subPropertyOf" , statement[2]])
            elif isinstance(statement[2], Literal):
                writer.writerow([statement[0],statement[1], statement[2]])
    del globals()['graph']

def get_fraud(size): 
    
    if not os.path.exists(anomaly_support.triples_fraud):
        print("Retrieving Fraud Simulation Data.")
        fr = pd.read_csv(anomaly_support.raw_fraud)

        # convert to json objects
        fr['a'] = [json.loads(a) for a in fr['a']]
        fr['b'] = [json.loads(b) for b in fr['b']]

        a_node = pd.json_normalize(fr['a'])
        b_node = pd.json_normalize(fr['b'])

        # save all entities features for later use
        (a_node + b_node).to_csv(anomaly_support.fraud_entities, index=False)

        # redefine what the subject/object is 
        # basing it on ID as nodes of different types are included 
        fr['subject'] = a_node['id']
        fr['SubjectEntityType'] = [set(x) for x in a_node.labels]

        fr['object'] = b_node['id']
        fr['ObjectEntityType'] = [set(x) for x in b_node.labels]

        fr['predicate'] = [x.lower() for x in fr['TYPE(r)']]
            
        fr[['subject', 'SubjectEntityType', 'predicate', 'object', 'ObjectEntityType']].to_csv(anomaly_support.triples_fraud, index=False)

    else: 
        print("Your data is clean.")

def get_yago(size): 

    # download data if it is not there
    if not os.path.exists('../assets_kraft/yago-1.0.0-turtle.ttl'):
        print("Downloading YAGO KG")
        response = requests.get('https://yago-knowledge.org/data/yago1/yago-1.0.0-turtle.7z')
        with open("../assets_kraft/yago-1.0-turtle.7z", 'wb') as yago:
            yago.write(response.content)

        print("Extracting the downloaded KG")
        with py7zr.SevenZipFile('../assets_kraft/yago-1.0-turtle.7z', mode='r') as extyago:
            extyago.extractall(path='../assets_kraft')
    else: 
        print("Your data has been downloaded.")

    if (not os.path.exists(anomaly_support.triples_yago) ) | (not os.path.exists(anomaly_support.yago_nodes)):
        print("Populating the graph")
        global graph
        graph = Graph()
        graph.parse('../assets_kraft/yago-1.0.0-turtle.ttl', format='ttl')

        # transitions to dataframe 
        convert_to_graph(size)
    else: 
        print("Your data has been converted to a dataframe.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='Anomaly Detection: Data Loading', 
                        description='You have the opportunity to load a unique dataset into this anomaly detector.')
    parser.add_argument("-d", dest='dataset', type=str, default='YAGO', 
                        help='Choose which dataset you are interested in evaluating.')
    parser.add_argument("-s", dest='sample_size', type=str, default='100', 
                        help='Recieve a random sample size in percentage (for use in testing).')
    args = parser.parse_args()

    dataset_options = {
        'YAGO' : get_yago,
        'fraud' : get_fraud
        # 'No' : define_your_own_kg
    }

    dataset_options[args.dataset](args.sample_size)

    print("---------------------")
    print("All data has been loaded.")
    print("---------------------")