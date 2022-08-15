'''
Generates a set of features for a knowledge graph based on the relative frequencies of the entities and entity types. 
Has the ability to remove correlated features, and generate customized features based on knowledge graph subject matter. 

INPUT: .csv with triple (subject, predicate, object) and subject/object entity types 
OUTPUT: .csv of 19+ features generated

Note: 
- Adopted from Asara Senaratne (https://github.com/AsaraSenaratne/anomaly-detection-kg)
- pathways to read/write files should be changed within anomaly_support file
'''

from collections import Counter
import numpy as np
import os

import networkx as nx
from tqdm import tqdm 
tqdm.pandas()
# import pandas
import modin.pandas as pd
from modin.config import ProgressBar
ProgressBar.enable()

import anomaly_support
import custom_features

def pairing_occurance_helper(grouping_to, df_links): 

    grouping_counts = df_links.groupby(grouping_to).size().to_frame().reset_index()
    x = df_links.merge(grouping_counts, on=grouping_to, how='left')[0]
    return x
    
def edge_degrees(df_links): 

    counts_subjects = Counter(list(df_links['subject']))
    counts_objects = Counter(list(df_links['object']))
    df_links['SubjectOutDeg'] = df_links['subject'].map(counts_subjects)
    df_links['SubjectInDeg'] = df_links['subject'].map(counts_objects)
    df_links['ObjectOutDeg'] = df_links['object'].map(counts_subjects)
    df_links['ObjectInDeg'] = df_links['object'].map(counts_objects)

    return df_links 

def occurances(df_links): 

    # number of times a full pairing occurs 
    groupings = {'EntityPredOccur' :  ['SubjectEntityType', 'predicate', 'ObjectEntityType'], 
                'PredEntityOccur' : ['SubjectEntityType','ObjectEntityType','predicate'], 
                'PredEntityTypeWithSubject' : ['SubjectEntityType','predicate'], 
                'PredEntityTypeWithObject'  : ['ObjectEntityType','predicate'], 
                'SubPredOccur' : ['subject','predicate'], 
                'PredObjOccur' : ['predicate','object'], 
                'SubObjOccur' : ['subject','object'], 
                'DupTriples' : ['subject', 'predicate','object']
                }
    
    for i in list(groupings.keys()): 
        df_links[i] = pairing_occurance_helper(groupings[i], df_links)

    # occurances for individual predicates
    df_links['PredOccur'] = df_links['predicate'].map(Counter(list(df_links['predicate'])))
    df_links['CountSubjectEntityType'] = df_links['SubjectEntityType'].map(Counter(list(df_links['SubjectEntityType'])))
    df_links['CountObjectEntityType'] = df_links['ObjectEntityType'].map(Counter(list(df_links['ObjectEntityType'])))
    
    return df_links

def corroborative_paths(df_links):
    #this method checks for the existence of alternative knowledge paths.
    label_count = {}
    G = nx.DiGraph()

    # building a graph
    print("Building a graph")
    [G.add_edges_from([(x, y)]) for x, y in tqdm(zip(df_links["subject"], df_links["object"]))]
   
    df_links['CorrPaths'] = [len(list(nx.all_simple_paths(G, x, y, cutoff=3))) for x, y in tqdm(zip(df_links["subject"], df_links["object"]))]
    
    return df_links, G

def feature_reduction(df):
    
    print("Inside feature reduction")
    df_filterd = df.drop(columns=['subject', 'predicate', 'object', 'SubjectEntityType','ObjectEntityType', 
                                    'Unnamed: 0', 'properties.globalStep', 'properties.step',
                                    'properties.ts', 'properties.fraud'], errors='ignore')
    df_filterd.replace(['1','0','True','False',True,False],[1,0,1,0,1,0], inplace=True)
    df_filterd = df_filterd.astype(np.float64)

    #Apparently this is actually the fastest way to do it
    for col in df_filterd.columns:
        count_unique = len(df[col].unique())
        if count_unique == 1:
            df_filterd.drop(col, inplace=True, axis=1)

    return df_filterd
    # columns = list(df_filterd.columns)
    # corr_feature_list = []
    # corr_filterd = df_filterd.corr()
    # np.fill_diagonal(corr_filterd.to_numpy(), 0)
    # corr_feature_list = corr_filterd[corr_filterd >= 1].dropna(how = 'all',axis = 1).columns.to_list()
    # return remove_corr_features(corr_feature_list, df_filterd, df)
   
# def remove_corr_features(corr_feature_list, df_filterd, df):
#     print("Correlated Features: ", corr_feature_list)

#     return gen_binary_feature(df_filterd, df)

    # features_to_remove  = [input("Enter the features to remove seperated by a comma without spaces: ")]
    # if features_to_remove[0] == '':
    #     return gen_binary_feature(df_filterd, df)
    # else:
    #     for feature in features_to_remove:
    #         df_filterd.drop(feature, inplace=True, axis=1)
    #     return gen_binary_feature(df_filterd, df)

# def gen_binary_feature(df_filterd, df):
#     print("inside binary_features")
#     columns = df_filterd.columns
#     for column in tqdm(columns):
#         med = df_filterd[column].median()
#         df["Freq" + column] = [1 if x > med else 0 for x in df_filterd[column]]

#     return df

def main(override, custom): 

    if not os.path.exists(anomaly_support.model_features) or override:
        print("Generating features of KG")

        df_links = pd.read_csv(anomaly_support.model_data)  

        if not set(['SubjectEntityType', 'predicate', 'ObjectEntityType', 'object', 'subject']).issubset(df_links.columns):
            print("The passed dataset does not have the full extent of triples needed to evaluate.")
            raise Exception(ValueError)

        # generating all of the requested features 
        print("Calculating edge degrees")
        df_links = edge_degrees(df_links)
        print("Generating cooccurances of entities")
        df_links = occurances(df_links)
        print("Building corroborative paths")
        df_links, G = corroborative_paths(df_links)
        df_links.to_csv(anomaly_support.model_data, index=False)

        if custom: 
            # use G to generate idea of centrality of graph 
            # generating custom subject matter features 
            try: 
                df_links = custom_features.subject(df_links, G)
                df_links.to_csv(anomaly_support.model_data, index=False)
            except: 
                print("there was an error with customization")
            # generating temporal based features 

        # TODO: normalize dataset 

        print("Reducing features based on relevance.")
        df_reduced = feature_reduction(df_links.copy())

        df_reduced.to_csv(anomaly_support.model_features, index=False)

        print("---------------------")
        print("Features have been generated.")
        print("---------------------")
    
    else: 
        print("Features have previously been generated.")

if __name__ == '__main__':
    main(False, True)

