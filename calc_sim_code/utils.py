import os
import pickle

def save_dataframes(dataframes, output_file="dataframes.pickle"):
    with open(output_file, 'wb') as f:
        pickle.dump(dataframes, f)

def load_dataframes(pickle_file):
    with open(pickle_file, 'rb') as f:
        return pickle.load(f)
