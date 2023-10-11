from bs4 import BeautifulSoup
import requests
import time
import random as ran
import sys
import pandas as pd
import  numpy as np
from warnings import warn


def scrape():

    # Note this takes about 40 min to run if np.arange is set to 9951 as the stopping point.

    pages = np.arange(1, 10000, 50) # Last time I tried, I could only go to 10000 items because after that the URI has no discernable pattern to combat webcrawlers; I just did 4 pages for demonstration purposes. You can increase this for your own projects.
    headers = {'Accept-Language': 'en-US,en;q=0.8'} # If this is not specified, the default language is Mandarin

    #initialize empty lists to store the variables scraped
    titles = []
    years = []
    ratings = []
    genres = []
    runtimes = []
    imdb_ratings = []
    imdb_ratings_standardized = []
    metascores = []
    votes = []

    for page in pages:

       #get request for sci-fi
       response = requests.get("https://www.imdb.com/search/title?genres=sci-fi&"
                      + "start="
                      + str(page)
                      + "&explore=title_type,genres&ref_=adv_prv", headers=headers)

       #sleep(randint(8,15))

       #throw warning for status codes that are not 200
       if response.status_code != 200:
           warn('Request: {}; Status code: {}'.format(requests, response.status_code))

       #parse the content of current iteration of request
       page_html = BeautifulSoup(response.text, 'html.parser')

       movie_containers = page_html.find_all('div', class_ = 'lister-item mode-advanced')

       #extract the 50 movies for that page
       for container in movie_containers:

           #conditional for all with metascore
           if container.find('div', class_ = 'ratings-metascore') is not None:
               #title
               title = container.h3.a.text
               titles.append(title)

               if container.h3.find('span', class_= 'lister-item-year text-muted unbold') is not None:

                 #year released
                 year = container.h3.find('span', class_= 'lister-item-year text-muted unbold').text # remove the parentheses around the year and make it an integer
                 years.append(year)

               else:
                 years.append(None) # each of the additional if clauses are to handle type None data, replacing it with an empty string so the arrays are of the same length at the end of the scraping

               if container.p.find('span', class_ = 'certificate') is not None:

                 #rating
                 rating = container.p.find('span', class_= 'certificate').text
                 ratings.append(rating)

               else:
                 ratings.append("")

               if container.p.find('span', class_ = 'genre') is not None:

                 #genre
                 genre = container.p.find('span', class_ = 'genre').text.replace("\n", "").rstrip().split(',') # remove the whitespace character, strip, and split to create an array of genres
                 genres.append(genre)

               else:
                 genres.append("")

               if container.p.find('span', class_ = 'runtime') is not None:

                 #runtime
                 time = int(container.p.find('span', class_ = 'runtime').text.replace(" min", "")) # remove the minute word from the runtime and make it an integer
                 runtimes.append(time)

               else:
                 runtimes.append(None)

               if float(container.strong.text) is not None:

                 #IMDB ratings
                 imdb = float(container.strong.text) # non-standardized variable
                 imdb_ratings.append(imdb)

               else:
                 imdb_ratings.append(None)

               if container.find('span', class_ = 'metascore').text is not None:

                 #Metascore
                 m_score = int(container.find('span', class_ = 'metascore').text) # make it an integer
                 metascores.append(m_score)

               else:
                 metascores.append(None)

               if container.find('span', attrs = {'name':'nv'})['data-value'] is not None:

                 #Number of votes
                 vote = int(container.find('span', attrs = {'name':'nv'})['data-value'])
                 votes.append(vote)

               else:
                   votes.append(None)
    return titles, years, ratings, genres, runtimes, imdb_ratings, metascores, votes

def transform(titles, years, ratings, genres, runtimes, imdb_ratings, metascores, votes):
    df = pd.DataFrame({'movie': titles,
                          'year': years,
                          'rating': ratings,
                          'genre': genres,
                          'runtime_min': runtimes,
                          'imdb': imdb_ratings,
                          'metascore': metascores,
                          'votes': votes}
                          )

    df.loc[:, 'year'] = df['year'].str[-5:-1] # two more data transformations after scraping
    # Drop 'ovie' bug
    # Make year an int
    df['n_imdb'] = df['imdb'] * 10
    df = df.loc[df['year'] != 'ovie'] # One small issue with the scrape on these two movies so just dropping those ones.
    df.loc[:, 'year'] = pd.to_numeric(df['year'])
    df.to_csv('movies_.csv')

