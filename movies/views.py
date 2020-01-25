from configparser import ConfigParser
from django.shortcuts import render
import tmdbsimple as tmdb
import os
import pandas as pd
import numpy as np
import pickle

smd = pd.read_csv("movies/soup.csv")

file = open("movies/model.pickle", "rb")
pkl = pickle.load(file)

config = ConfigParser()
config.read('movies/config.cfg')
tmdb.API_KEY = config['tmdb']['API_KEY']

# Create your views here.
def home(request):
    """This is a function-based view to serve
    the movie list for a particular search query,
    using tmdbsimple API calls.

    Params:
        request: request from the front-end API call

    Returns:
        render method at the movie.html endpoint with
        the required search results.
    """
    query = str(request.GET.get('query', ''))
    if query != '':
        search_result = tmdb.Search().movie(query=query)['results']
        frontend = {
            "search_result": sorted(search_result, key=lambda x: x['popularity'], reverse=True),
            "has_result": (search_result != [])
        }
    else:
        frontend = {
            "search_result": [],
            "has_result": False
        }
    return render(request, "movie.html", frontend)

def recomendations(request, id = None):
    """This is a function-based view to serve
    the movie list for a particular search query,
    using tmdbsimple API calls.

    Params:
        request: request from the front-end API call

    Returns:
        render method at the movie.html endpoint with
        the required search results.
    """
    #smd = smd.reset_index()
    # indices = pd.Series(smd.index, index=smd['title'])

    idx = smd[smd['id'] == int(id)].index

    def get_recommendations(id):
        sim_scores = list(enumerate(pkl[id]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:31]
        movie_indices = [i[0] for i in sim_scores]
        return smd.iloc[movie_indices]



    qualified = get_recommendations(idx[0])
    #qualified = qualified[(qualified['vote_count'] > 100) & (qualified['vote_average'] > 6.5)]
    qualified = qualified['title'].tolist()

    search_result = []
    count = 0
    i = 0
    while(count < 6 and i < len(qualified)):
        search_result.append(tmdb.Search().movie(query=qualified[i])['results'][0])
        count += 1  
        i += 1

    frontend = {
        "search_result": search_result,
        "has_result": (search_result != [])
    }

    return render(request, "movie.html", frontend)


def details(request, id=None):
    """This is a function-based view to serve 
    the movie details for a particular list click,
    using tmdbsimple API calls.

    Params:
        request: request from the front-end API call
        id (int): id of the movie clicked on

    Returns:
        render method at the details.html endpoint with
        the required movie details.
    """
    movie = tmdb.Movies(id)
    trailers = list(filter(lambda v: v['type'] == 'Trailer', movie.videos()['results']))
    teasers = list(filter(lambda v: v['type'] == 'Teaser', movie.videos()['results']))
    keywords = movie.keywords()['keywords']
    from pprint import pprint
    pprint(movie.reviews()['results'])
    frontend = {
        "info": movie.info(),
        "year": movie.info()['release_date'][:4],
        "cast": movie.credits()['cast'][:15],
        "crew": movie.credits()['crew'][:15],
        "trailers": trailers,
        "teasers": teasers,
        "keywords": keywords,
        "reviews": movie.reviews()['results'],
        "alt": movie.alternative_titles()['titles']
    }
    return render(request, "details.html", frontend)
