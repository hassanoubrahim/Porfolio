# app.py
import numpy as np
import pandas as pd
from dash import Dash, dcc, html,dependencies

data = (
    pd.read_csv("movies.csv")
    .assign(Date=lambda data: pd.to_datetime(data["year"]))
    .sort_values(by="year")
)



app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Movies Analytics"),
        html.P(
            children=(
                "Analyze the movies trend since 1973"
            ),
        ),


        html.Div(
            children=[
                html.Label("Select Year:"),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": year, "value": year} for year in np.flip(data['year'].unique())],
                    value="All"#data['year'].max(),
                ),
            ],
        ),

       dcc.Graph(id="categories_counts"),
       dcc.Graph(
            figure={
                "data": [
                    {
                        "y": (data.groupby('year').size()),
                        "x": list(year for year in (data['year'].unique())),
                        "type": "bar",
                    },
                ],
                "layout": {
                    "title": "Movies by year",
                    "xaxis": {
                        "title": "year",
                        "tickmode": "array",
                    },
                    "yaxis": {"title": "Number of Movies"},
        },
            },
        ),
        html.Div(
            children=[
                html.Label('Select Year'),
                dcc.Dropdown(
                    id="top-year-dropdown",
                    options=[{"label": year, "value": year} for year in np.flip(data['year'].unique())],
                    value="all"
                ),
                html.Label('Select Top K'),
                dcc.Dropdown(
                    id="top-k-dropdown",
                    options=[{"label": k, "value": k} for k in [1, 5, 10, 25, 50, 100,500, 1000]],
                    value="all"
                ),
            ],
        ),
        dcc.Graph(id="top-k-movies"),

        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["year"],
                        "y": data["votes"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Movies by votes"},
            },
        ),

    ]
)

@app.callback(
    dependencies.Output("categories_counts", "figure"),
    [dependencies.Input("year-dropdown", "value")],
)
def update_graph(selected_year):
    categories = set()
    for genres in data['genre']:
        categories.update(genres.strip("[]").replace("'", "").split(", "))
    #print(categories)
    if isinstance(selected_year, int):
        filtered_data = data[data['year'] == int(selected_year)]
        categories_counts = {}
        for cat in categories:
            categories_counts[cat] = 0
        for genre in filtered_data['genre']:
            gre = genre.strip("[]").replace("'", "").split(", ")
        for g in gre:
            categories_counts[g] += 1
        total_movies =filtered_data.shape[0]
    else:
        #movies_by_category = data[data['genre'].apply(lambda x: any(category in x for category in categories))]
        categories_counts = {}
        for cat in categories:
            categories_counts[cat] = 0
        for genre in data['genre']:
            gre = genre.strip("[]").replace("'", "").split(", ")
            for g in gre:
                categories_counts[g] += 1
        total_movies = data.shape[0]




    #print(categories_counts.values())
    #print(categories_counts.keys())

    return {
        "data": [
            {
                "x": list(categories_counts.keys()),
                "y": list(categories_counts.values()),
                "type": "bar",
            },
        ],
        "layout": {
            "title": "Movies by Categories : Total movies = {}, Year = {}".format(total_movies, selected_year),
            "xaxis": {
                "title": "Category",
                "tickmode": "array",
            },
            "yaxis": {"title": "Number of Movies"},
        },
    }

# Callback function for the top movies graph
@app.callback(
    dependencies.Output("top-k-movies", "figure"),
    [
        dependencies.Input("top-year-dropdown", "value"),
        dependencies.Input("top-k-dropdown", "value"),
    ],
)
def update_top_movies_graph(selected_year, k):
    sorted_data = data.sort_values('imdb', ascending=True)
    if selected_year != 'all':
        top_movies = sorted_data[sorted_data['year'] == selected_year]
        top_k_movies = top_movies.nlargest(top_movies.shape[0], 'imdb')[['movie', 'imdb']]

    if k != 'all':
        if selected_year != 'all':
            top_k_movies = top_movies.nlargest(int(k), 'imdb')[['movie', 'imdb']]
        else:
            top_k_movies = sorted_data.nlargest(int(k), 'imdb')[['movie', 'imdb']]
    else:
        top_k_movies = sorted_data.nlargest(sorted_data.shape[0], 'imdb')[['movie', 'imdb']]
    print(top_k_movies)
    return {
        "data": [
            {
                "x": top_k_movies['movie'],
                "y": top_k_movies['imdb'],
                "type": "line",
            },
        ],
        "layout": {
            "title": f"Top {k} Movies by Rating",
            "xaxis": {"title": "Movie"},
            "yaxis": {"title": "Rating"},
        },
    }

app.run_server(debug=True)
