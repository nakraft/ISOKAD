import sys
import os 
import time
import numpy as np
import modin.pandas as pd
import ray
ray.init()
from tqdm import tqdm
import argparse

from sklearnex import patch_sklearn
patch_sklearn()
from sklearn import preprocessing
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support

import anomaly_support

def model_training_svm(df): 

    for kernel in tqdm(['sigmoid', 'rbf', 'linear']): 
        print("Training on " + kernel)
        clf = OneClassSVM(kernel=kernel, verbose=True)
        #n_estimators = 1000
        #clf = BaggingClassifier(OneClassSVM(kernel=kernel), max_samples=1.0 / n_estimators, n_estimators=n_estimators)
        clf.fit(df)
        print('Fitting complete.')
        binary_outlier = clf.predict(df)
        df['score_outlier_' + kernel] = [round(x, 5) for x in tqdm(clf.decision_function(df))]
        df['binary_outlier_' + kernel] = binary_outlier
        # normalize values 
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
        df['score_normalized_' + kernel] = min_max_scaler.fit_transform(df['score_outlier_' + kernel].array.reshape(-1, 1))

    print("Model training complete.")
    return df 

def recognize_abnormal_behavior(df): 

    df['anomylous_counts'] = df[['binary_outlier_' + x for x in ['rbf', 'sigmoid', 'linear']]].sum(axis=1)
    df['anomylous_scores'] = df[['score_normalized_' + x for x in ['rbf', 'sigmoid', 'linear']]].sum(axis=1)
    df['average_score'] = [x / 3 for x in df['anomylous_scores']]
    print(str(df['average_score'].sum() / len(df)) + " percent is the average anomalous score.")

    df['decision'] = [1 if average_score <=0 else 0 for average_score in df['average_score']]

    return df

def evaluate_model(df, ground_truth, model_type): 

    print("Confusion Matrix: ")
    print(confusion_matrix(ground_truth, df[model_type]))
    print("Precision.... Recall... FScore... Support | Binary Labeling")
    print(precision_recall_fscore_support(ground_truth, df[model_type], average='binary'))
    print("Precision.... Recall... FScore... Support | Micro Labeling")
    print(precision_recall_fscore_support(ground_truth, df[model_type], average='micro'))


def svm(evaluate): 

    start_time = time.time()
    print("SVM model:")
    # gathering data 
    df = pd.read_csv(anomaly_support.model_features).iloc[:, anomaly_support.initial_attribute_count:]

    # training model 
    df = model_training_svm(df)
    df.to_csv(anomaly_support.model_results, index=False)

    # evaluation
    df = recognize_abnormal_behavior(df)
    df = df.sort_values(by=["average_score"], ascending=True)
    df.to_csv(anomaly_support.model_results, index=False)

    if evaluate: 
        ground_truth = pd.read_csv(anomaly_support.model_features)[anomaly_support.ground_truth]
        ground_truth.replace({'False':0, 'True':1, False: 0, True: 1, np.nan: 0}, inplace = True)
        df = evaluate_model(df, ground_truth, "svm_decision")

    return (time.time() - start_time, np.nan)

def model_training_forest(df, contamination): 

    ifm = IsolationForest(n_estimators=100, max_samples='auto', contamination = contamination, random_state = 96, verbose=True) 
    ifm.fit(df)
    print("Completed fitting.")
    score_outlier = ifm.decision_function(df)
    df.insert(1, 'forest_score_outlier', score_outlier)

    print(str((df['forest_score_outlier'] < 0).sum()) + " out of " + str(len(df)) + " were decided as anomalous.")
    df.insert(2, 'forest_decision', [1 if x <=0 else 0 for x in df['forest_score_outlier']])

    print("Model training complete.")
    return df

def forest(evaluate, subject_feature): 

    start_time = time.time()
    print("Forest model:")
    # gathering data 
    df_org = pd.read_csv(anomaly_support.model_data)

    if not subject_feature: 
        df_org.drop(columns=['distance_from_target', 'distance_to_target'], inplace=True, errors='ignore')
        custom = 2
    else: 
        custom = 0
        print("Custom features are being used in this analysis.")
    df = df_org.iloc[:, (df_org.shape[1] - (anomaly_support.initial_attribute_count - custom)):]

    for col in df.columns: 
        col_mean = df[col].mean()
        if pd.notna(col_mean): 
            df[col] = df[col].fillna(col_mean)
    
    # training model 
    df = model_training_forest(df, contamination='auto')

    # add in original data facts 
    decisions_org = pd.concat([df_org.iloc[:, 0:(len(df_org.columns) - anomaly_support.initial_attribute_count)], df], axis=1)
    
    # STORAGE OF DATA IS HORENDOUS... TODO: FIX
    

    if os.path.exists(anomaly_support.model_results):
        # evaluation
        num = 0
        for file in os.listdir("../results_kraft"):
            if file.startswith((anomaly_support.model_results).split(".csv")[0][0:-1].split("/")[-1]):
                # get maximum file there 
                val = int(file.split(".csv")[0][-1:])
                if num < val: 
                    num = val
                    print(num)
        new_results = anomaly_support.model_results.split(".csv")[0][0:-1] + str(num + 1) + ".csv"
    else: 
        new_results = anomaly_support.model_results
        
        # to_save = list(set(results.columns).difference(set(decisions_org.columns)))
        # dup_columns = list(set(decisions_org.columns).intersection(set(results.columns)))
        # dup_columns = [x for x in dup_columns if ("forest" in x) | ("svm" in x)]

        # if len(to_save) != 0: 
        #     [decisions_org.insert(0, to_save_var, results[to_save_var]) for to_save_var in to_save]
        # if len(dup_columns) != 0: 
        #     decisions_org.rename(columns = dict(zip(dup_columns, [x + "1" for x in dup_columns])), inplace=True) 
        #     [decisions_org.insert(0, dup_columns_var, results[dup_columns_var]) for dup_columns_var in dup_columns]
    
    if "svm_anomaly_score" in list(decisions_org.columns): 
        decisions_org = decisions_org.sort_values(by=["forest_anomaly_score", "svm_anomaly_score"], ascending=True)
    else:
        decisions_org = decisions_org.sort_values(by=["forest_anomaly_score", "svm_anomaly_score"], ascending=True)
   
    # export decision report
    print("Your results are saved here: " + new_results)
    decisions_org.to_csv(new_results, index=False)

    if evaluate: 
        ground_truth = df_org[anomaly_support.ground_truth]
        ground_truth.replace({'False':0, 'True':1, False: 0, True: 1, np.nan: 0}, inplace = True)
        df = evaluate_model(df, ground_truth, "forest_decision")

    return (np.nan, time.time() - start_time)

def run_models(evaluation): 

    print("---------------------")
    print("Training models.")
    print("---------------------")

    svm_time = svm(evaluation)
    forest_time = forest(evaluation)

    return (svm_time[0], forest_time[1])

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='Anomaly Modeling', 
                        description='Utilize unsupervised SVMs to train a model recognizing anomalies.')
    parser.add_argument("-e", '--evaluate', action = "store_true",  
                        help='Does this model have an evaluation feild?')
    parser.add_argument("-d", dest='dataset', type=str, default='YAGO', 
                        help='Choose which dataset you are interested in evaluating.')
    parser.add_argument("-m", dest='model', type=str, default='all', 
                        help='Choose which model you are interested in using.')
    args = parser.parse_args()

    anomaly_support.set_data(args.dataset)

    model = {
        'svm' : svm,
        'forest' : forest,
        'all' : run_models
    }
    
    svm_time, forest_time = model[args.model](args.evaluate)

    print("Here is your performance report:")
    if pd.notna(svm_time): 
        print("SVM Model Training, Predictions and Evaluation: " + str(svm_time))
    if pd.notna(forest_time): 
        print("Isolation Forest Model Training, Predictions and Evaluation: " + str(forest_time))
