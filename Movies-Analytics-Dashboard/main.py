
from scrapFunctions import scrape, transform


titles, years, ratings, genres, runtimes, imdb_ratings, metascores, votes = scrape()

transform(titles, years, ratings, genres, runtimes, imdb_ratings, metascores, votes)

