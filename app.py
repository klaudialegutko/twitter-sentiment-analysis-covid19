from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import itertools
import math
import base64
from flask import Flask
import datetime
import re
import nltk
import os
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import mysql.connector
import string
import time
import datetime


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.title = 'Real-Time Twitter Analysis'
server = server

app.layout = html.Div(children=[
    html.H2('Real-time Twitter Analysis', style={
        'textAlign': 'center'
    }),
    html.H4('(Last updated: Apr 12, 2020)', style={
        'textAlign': 'right'
    }),


    html.Div(id='live-update-graph'),
    html.Div(id='live-update-graph-bottom'),

# ABOUT ROW
    html.Div(
        className='row',
        children=[
            html.Div(
                className='three columns',
                children=[
                    html.P(
                    'Data extracted from:'
                    ),
                    html.A(
                        'Twitter API',
                        href='https://developer.twitter.com'
                    )
                ]
            ),
            html.Div(
                className='three columns',
                children=[
                    html.P(
                    'Made with:'
                    ),
                    html.A(
                        'Dash / Plot.ly',
                        href='https://plot.ly/dash/'
                    )
                ]
            ),
            html.Div(
                className='three columns',
                children=[
                    html.P(
                    'Author:'
                    ),
                    html.A(
                        'Klaudia Legutko',
                        href='https://www.linkedin.com/in/klaudia-legutko/'
                    )
                ]
            )
        ], style={'marginLeft': 70, 'fontSize': 16}
    ),

    dcc.Interval(
        id='interval-component-slow',
        interval=1*10000, # in milliseconds
        n_intervals=4
    )
    ], style={'padding': '20px'})

# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'children'),
            [Input('interval-component-slow', 'n_intervals')])
def update_graph_live(n):

    #Connecting to database
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YourPassword",
    database="DBname",
    charset = 'utf8'
)

    timenow = (datetime.datetime.utcnow() - datetime.timedelta(hours=0, minutes=20)).strftime('%Y-%m-%d %H:%M:%S')
    query = "SELECT username, created_at, tweet, place FROM tweets2 WHERE created_at >= '{}' ".format(timenow)
    df = pd.read_sql(query, con=mydb)
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x - datetime.timedelta(hours=7))

    #Cleaning tweets
    stop_words=set(stopwords.words("english"))
    def TxtProcessing(text):

        text  = "".join([char for char in text if char not in string.punctuation])
        text = re.sub('[0-9]+', '', text)
        text = re.sub(r'@[A-Za-z0-9]+','',text)
        text = re.sub('https?://[A-Za-z0-9./]+','', text)
        text = re.sub('[^a-zA-Z]',' ', text)
        text = text.replace('RT ', ' ').replace('amp', ' ').replace('via', ' ')
        text = text.lower()
        text = word_tokenize(text)
        text = [word for word in text if word not in stop_words]

        return text

    df['tweet'] = df['tweet'].apply(lambda x: TxtProcessing(x))

    #Sentiment
    df['tweet'] = df['tweet'].astype(str)
    df['sentiment'] = df['tweet'].apply(lambda tweet: TextBlob(tweet).sentiment)
    #Split Sentiment into two separate Cols
    df['polarity'] = df['sentiment'].apply(lambda x: x[0])
    df['subjectivity'] = df['sentiment'].apply(lambda x: x[1])

    result = df.groupby([pd.Grouper(key='created_at', freq='10s'), 'polarity']).count().unstack(fill_value=0).stack().reset_index()
    result = result.rename(columns=
    { "username": "Num of CORONAVIRUS mentions",
      "created_at":"Time in UTC" })
    time_series = result["Time in UTC"][result['polarity']==0].reset_index(drop=True)

#Create Scatter
    children = [
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='crossfilter-indicator-scatter',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=time_series,
                                    y=result["Num of CORONAVIRUS mentions"][result['polarity']==-1].reset_index(drop=True),
                                    name="Polarity = -1",
                                    opacity=0.8,
                                    mode='lines',
                                    line=dict(width=0.5, color='rgb(128,0,0)'),
                                    stackgroup='one'
                                ),
                                go.Scatter(
                                    x=time_series,
                                    y=result["Num of CORONAVIRUS mentions"][result['polarity']==-0.5].reset_index(drop=True),
                                    name="Polarity = -0.5",
                                    opacity=0.8,
                                    mode='lines',
                                    line=dict(width=0.5, color='rgb(255,99,71)'),
                                    stackgroup='two'
                                ),
                                go.Scatter(
                                    x=time_series,
                                    y=result["Num of CORONAVIRUS mentions"][result['polarity']==0].reset_index(drop=True),
                                    name="Polarity = 0",
                                    opacity=0.8,
                                    mode='lines',
                                    line=dict(width=0.5, color='rgb(240,230,140)'),
                                    stackgroup='three'
                                ),
                                go.Scatter(
                                    x=time_series,
                                    y=result["Num of CORONAVIRUS mentions"][result['polarity']==0.5].reset_index(drop=True),
                                    name="Polarity = 0.5",
                                    opacity=0.8,
                                    mode='lines',
                                    line=dict(width=0.5, color='rgb(154,205,50)'),
                                    stackgroup='four'
                                ),
                                go.Scatter(
                                    x=time_series,
                                    y=result["Num of CORONAVIRUS mentions"][result['polarity']==1].reset_index(drop=True),
                                    name="Polarity = 1",
                                    opacity=0.8,
                                    mode='lines',
                                    line=dict(width=0.5, color='rgb(0,100,0)'),
                                    stackgroup='five'
                                )
                            ]
                        }
                    )
                ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 0 0 20'})
            ]),
        ]
    return children

@app.callback(Output('live-update-graph-bottom', 'children'),
            [Input('interval-component-slow', 'n_intervals')])
def update_graph_bottom_live(n):

    #Connecting to database
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YourPassword",
    database="DBname",
    charset = 'utf8'
)
    timenow = (datetime.datetime.utcnow() - datetime.timedelta(hours=0, minutes=20)).strftime('%Y-%m-%d %H:%M:%S')
    query = "SELECT username, created_at, tweet, place FROM tweets2 WHERE created_at >= '{}' ".format(timenow)
    df = pd.read_sql(query, con=mydb)
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x - datetime.timedelta(hours=7))

    #Geodistribution of tweets
    geo_dist = pd.DataFrame(df['place'], columns=['place']).dropna().reset_index()
    geo_dist = geo_dist.groupby('place').count().rename(columns={"index": "number"}).sort_values(by=['number'], ascending=False).reset_index()
    geo_dist["num"] = geo_dist["number"]

    #Cleaning tweets
    stop_words=set(stopwords.words("english"))
    def TxtProcessing(text):

        text  = "".join([char for char in text if char not in string.punctuation])
        text = re.sub('[0-9]+', '', text)
        text = re.sub(r'@[A-Za-z0-9]+','',text)
        text = re.sub('https?://[A-Za-z0-9./]+','', text)
        text = re.sub('[^a-zA-Z]',' ', text)
        text = text.replace('RT ', ' ').replace('amp', ' ').replace('via', ' ')
        text = text.lower()
        text = word_tokenize(text)
        text = [word for word in text if word not in stop_words]

        return text

    df['tweet'] = df['tweet'].apply(lambda x: TxtProcessing(x))


    full_list = []
    for elmnt in df['tweet']:
        full_list += elmnt

    val_counts = pd.Series(full_list).value_counts()
    words = val_counts.to_frame().reset_index()
    most_common_words = words.rename(columns={'index': 'Word', 0: 'Frequency'})
    most_common_words = most_common_words.head(10)

    #Sentiment
    df['tweet'] = df['tweet'].astype(str)
    df['sentiment'] = df['tweet'].apply(lambda tweet: TextBlob(tweet).sentiment)
    #Split Sentiment into two separate Cols
    df['polarity'] = df['sentiment'].apply(lambda x: x[0])
    df['subjectivity'] = df['sentiment'].apply(lambda x: x[1])

    result = df.groupby([pd.Grouper(key='created_at', freq='10s'), 'polarity']).count().unstack(fill_value=0).stack().reset_index()
    result = result.rename(columns=
    { "username": "Num of CORONAVIRUS mentions",
      "created_at":"Time in UTC" })
    time_series = result["Time in UTC"][result['polarity']==0].reset_index(drop=True)

    children = [
                html.Div([
                    dcc.Graph(
                        id='x-time-series',
                        figure = {
                            'data':[
                                go.Bar(
                                x=most_common_words["Word"],
                                y=most_common_words["Frequency"],
                                name="Most Common Words",
                                #orientation = 'h',
                                marker_line_width=1.5,
                                opacity=0.8,
                                marker_color = 'rgba(255, 50, 50, 0.6)'),

                            ],
                            'layout':{
                                'title': "Most Common Words",
                                'hovermode':"closest"
                            }
                        }
                    )
                ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 0 0 20'}),
                html.Div([
                    dcc.Graph(
                        id='y-time-series',
                        figure = {
                            'data':[
                                go.Choropleth(
                                    locations=geo_dist['place'], # Spatial coordinates
                                    z = geo_dist['num'].astype(float), # Data to be color-coded
                                    locationmode = 'country names',
                                    colorbar_title = "Number of Tweets",
                                    colorscale = ["#fdf7ff", "#800000"],
                                    geo = 'geo'

                                )
                            ],
                            'layout': {
                                'title': "Geographic Segmentation",
                                'geo':{'scope':'world'}
                            }
                        }
                    )
                ], style={'display': 'inline-block', 'width': '49%'})
            ]

    return children


if __name__ == '__main__':
    app.run_server(debug=True)
