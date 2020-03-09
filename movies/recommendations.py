from configparser import ConfigParser
import pandas as pd
import pickle

file = open("movies/model.pickle", "rb")
pkl = pickle.load(file)

def init_files():
    smd = pd.read_csv("movies/soup.csv")
    return smd

def get_recommendations(id):
    sim_scores = list(enumerate(pkl[id]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    return smd.iloc[movie_indices]



