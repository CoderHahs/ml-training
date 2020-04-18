import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objects as go
import pandas as pd
import requests
import numpy as np
from flask import request

# initialize app
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.title = 'COVID-19 Report'

server = app.server

first_time = True

# summary data
r = requests.get("https://api.covid19api.com/summary")
summary_data = r.json()
summary_df = pd.DataFrame(summary_data['Countries'])
summary_df = summary_df.sort_values(by=['TotalConfirmed'], ascending=False).drop(columns=['Slug'])
summary_table = go.Figure(data=[go.Table(
    header=dict(values=['Country', 'New Confirmed', 'Total Confirmed', 'New Deaths', 'Total Deaths', 'New Recovered', 'Total Recovered'],
                align='left'),
    cells=dict(values=[summary_df.Country, summary_df.NewConfirmed, summary_df.TotalConfirmed,
			   summary_df.NewDeaths, summary_df.TotalDeaths, summary_df.NewRecovered, summary_df.TotalRecovered],
               align='left'))
])

# get list of countries
r = requests.get("https://api.covid19api.com/countries")
countries = pd.DataFrame(r.json()).sort_values(by='Country')

# initial chart pulling
# r = requests.get('http://ipinfo.io/json')
iso = 'CA'
slug = countries[countries['ISO2'] == iso]['Slug'].values[0]
ip_country = countries[countries['ISO2'] == iso]['Country'].values[0]
r = requests.get('https://api.covid19api.com/country/'+slug)
initial_data = pd.DataFrame(r.json())[['Date', 'Confirmed', 'Deaths', 'Recovered']].groupby('Date').sum().reset_index()
initial_data

# world totals
r = requests.get("https://api.covid19api.com/world/total")
world_data = r.json()

app.layout = html.Div(children=[
    html.H1(
        children='COVID-19 Report',
        style={'textAlign': 'center', 'font-size': '40px'}
    ),

    html.Div(
    children='''A graphical report made to help understand the pandemic.
    Brought to you by Hrithik Shah.''',
    style={
            'textAlign': 'center',
        }
    ),
	html.Div([
            html.H2("World - ", style ={'display':'inline', 'font-size': '30px'}),
			html.H2("Total: "+str(world_data['TotalConfirmed']), style ={'display':'inline'}),
			html.H2("\tActive: "+str(world_data['TotalConfirmed'] - world_data['TotalDeaths']- world_data['TotalRecovered']), style ={'display':'inline', 'color': 'blue'}),
			html.H2("\tDeaths: "+str(world_data['TotalDeaths']), style ={'display':'inline', 'color': 'red'}),
			html.H2("\tRecovered: "+str(world_data['TotalRecovered']), style ={'display':'inline', 'color': 'green'}),
    	],
		style={'textAlign': 'center', 'padding':'10px 0px 10px 0px'}
	),
    html.Div([
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': i, 'value': i} for i in countries['Country']],
                value=ip_country
            )
    ]),
	html.Div([
        dcc.Graph(
            id='active-graph',
            figure={
                'data': [
                    {'x': initial_data['Date'], 'y': initial_data['Confirmed']- initial_data['Deaths']-initial_data['Recovered'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Active Cases - '+ip_country,
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of people still infected'},
                )
            }
        )],
		style={'maxWidth': '50%', "display": "inline-block"}
    ),
	html.Div([
        dcc.Graph(
            id='log-graph',
            figure={
                'data': [
                    {'x': initial_data['Date'], 'y': np.log(initial_data['Confirmed']- initial_data['Deaths']-initial_data['Recovered']), 'type': 'line'},
                ],
                'layout': dict(
                    title='Log of Active Cases - '+ip_country,
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Rate of people being infected'},
                )
            }
        )],
		style={'maxWidth': '50%', "display": "inline-block"}
    ),
    html.Div([
        dcc.Graph(
            id='confirmed-graph',
            figure={
                'data': [
                    {'x': initial_data['Date'], 'y': initial_data['Confirmed'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Confirmed Cases - '+ip_country,
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of total infections'},
                )
            }
        )],
        style={'width': '34%', 'display': 'inline-block'}
    ),
    html.Div([
        dcc.Graph(
            id='deaths-graph',
            figure={
                'data': [
                    {'x': initial_data['Date'], 'y': initial_data['Deaths'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Number of Deaths - '+ip_country,
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of deaths'},
                )
            }
        )],
        style={'display': 'inline-block', 'width': '33%'}
    ),
    html.Div([
        dcc.Graph(
            id='recovered-graph',
            figure={
                'data': [
                    {'x': initial_data['Date'], 'y': initial_data['Deaths'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Recovered Cases - '+ip_country,
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of recovered cases'},
                )
            }
        )],
        style={'display': 'inline-block', 'width': '33%'}
    ),
	html.Div([
		dcc.Graph(figure=summary_table)
		],
		style={"display": "block","margin-left": "auto","margin-right": "auto"}
	)
])

@app.callback(
    Output('confirmed-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_confirmed_graph (country_selected):
    slug = countries[countries['Country'] == country_selected]['Slug'].values[0]
    r = requests.get('https://api.covid19api.com/total/country/'+slug)
    dff = pd.DataFrame(r.json())[['Date', 'Confirmed', 'Deaths', 'Recovered']].groupby('Date').sum().reset_index()
    return {
        'data': [
            {'x': dff['Date'], 'y': dff['Confirmed'], 'type': 'line'},
        ],
        'layout': dict(
            title='Confirmed Cases - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of total infections'},
        )
    }

@app.callback(
    Output('deaths-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_deaths_graph (country_selected):
	slug = countries[countries['Country'] == country_selected]['Slug'].values[0]
	r = requests.get('https://api.covid19api.com/total/country/'+slug)
	dff = pd.DataFrame(r.json())[['Date', 'Deaths']].groupby('Date').sum().reset_index()
	return {
        'data': [
            {'x': dff['Date'], 'y': dff['Deaths'], 'type': 'line'},
        ],
        'layout': dict(
            title='Number of Deaths - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of deaths'},
        )
    }

@app.callback(
    Output('recovered-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_recovered_graph (country_selected):
	slug = countries[countries['Country'] == country_selected]['Slug'].values[0]
	r = requests.get('https://api.covid19api.com/total/country/'+slug)
	dff = pd.DataFrame(r.json())[['Date', 'Recovered']].groupby('Date').sum().reset_index()

	return {
        'data': [
            {'x': dff['Date'], 'y': dff['Recovered'], 'type': 'line'},
        ],
        'layout': dict(
            title='Recovered Cases - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of recovered cases'},
        )
    }

@app.callback(
    Output('log-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_log_graph (country_selected):
	slug = countries[countries['Country'] == country_selected]['Slug'].values[0]
	r = requests.get('https://api.covid19api.com/total/country/'+slug)
	dff = pd.DataFrame(r.json())[['Date', 'Confirmed', 'Deaths', 'Recovered']].groupby('Date').sum().reset_index()
	return {
        'data': [
            {'x': dff['Date'], 'y': np.log(dff['Confirmed']-dff['Deaths']-dff['Recovered']), 'type': 'line'},
        ],
        'layout': dict(
            title='Log of Active Cases - '+country_selected,
			xaxis={'title': 'Date'},
			yaxis={'title': 'Rate of people being infected'},
        )
    }

@app.callback(
    Output('active-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_active_graph (country_selected):
	slug = countries[countries['Country'] == country_selected]['Slug'].values[0]
	r = requests.get('https://api.covid19api.com/total/country/'+slug)
	dff = pd.DataFrame(r.json())[['Date', 'Confirmed', 'Deaths', 'Recovered']].groupby('Date').sum().reset_index()
	return {
        'data': [
            {'x': dff['Date'], 'y': dff['Confirmed']-dff['Deaths']-dff['Recovered'], 'type': 'line'},
        ],
        'layout': dict(
            title='Active Cases - '+country_selected,
			xaxis={'title': 'Date'},
			yaxis={'title': 'Number of people still infected'},
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
