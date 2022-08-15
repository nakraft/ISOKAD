import time 
import math

import pandas as pd 
import networkx as nx

import anomaly_support

def subject(df, G): 
    start_time = time.time()
    print("Let's identify if there are anomalous activities as relating to TTP:")

    # identify how far away every node is from the center and from the node of relevance
    # centrality = nx.betweenness_centrality(G, normalized = True, endpoints = False)
    # df['subject_centrality_metric'] = df['subject'].map(centrality)
    # df['object_centrality_metric'] = df['object'].map(centrality)
    # target_from_center = df.loc[df['subject'] == anomaly_support.target, 'subject_centrality_metric'].mean()
    # df['distance_target'] = math.abs(df['distance_target'] - target_from_center)
    
    
    # calculate the distance away from that location of the target 
    # gets the path from all nodes to the specific node of interest 
    subject_to_target = nx.shortest_path_length(G, source=None,
                target=anomaly_support.target)
    object_from_target = nx.shortest_path_length(G, source=anomaly_support.target, 
                target=None)

    df['distance_to_target'] = df['subject'].map(subject_to_target).fillna(0)
    df['distance_from_target'] = df['object'].map(object_from_target).fillna(0)

    return df
