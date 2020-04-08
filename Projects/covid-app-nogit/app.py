import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import requests

# initialize app
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.title = 'COVID-19 Report'

server = app.server

# pull all the data
r = requests.get("https://api.covid19api.com/all")
data = r.json()

r = requests.get("https://api.covid19api.com/summary")
summary_data = r.json()

# create dataframe
df = pd.DataFrame(data)
summary_df = pd.DataFrame(summary_data['Countries'])
summary_df = summary_df.sort_values(by=['TotalConfirmed'], ascending=False).drop(columns=['Slug'])

if isinstance(df, (pd.DatetimeIndex, pd.MultiIndex)):
	df = df.to_frame(index=False)

# remove any pre-existing indices for ease of use in the D-Tale code, but this is not required
df = df.reset_index().drop('index', axis=1, errors='ignore')
df.columns = [str(c) for c in df.columns]  # update columns to strings in case they are numbers
chart_data = pd.concat([
	df['Date'],
	df['Confirmed'],
	df['Deaths'],
	df['Recovered'],
	df['Active'],
	df['Country'],
], axis=1)
chart_data = chart_data.sort_values(['Country', 'Date'])
chart_data = chart_data.groupby(['Country', 'Date']).sum().reset_index()
chart_data = chart_data.dropna()
worldwide_grouped = chart_data.groupby(['Date']).sum().reset_index()
worldwide_grouped['Country'] = 'Worldwide'
chart_data = pd.concat([chart_data, worldwide_grouped], ignore_index=True)
countries = chart_data['Country'].unique()

app.layout = html.Div(children=[
    html.H1(
        children='COVID-19 Report',
        style={
            'textAlign': 'center',
            }
    ),

    html.Div(
    children='''A graphical report made to help understand the pandemic.
    Brought to you by Hrithik Shah.''',
    style={
            'textAlign': 'center',
        }
    ),
    html.Div([
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': i, 'value': i} for i in countries],
                value='Worldwide'
            )
    ]),
    html.Div([
        dcc.Graph(
            id='confirmed-graph',
            figure={
                'data': [
                    {'x': worldwide_grouped['Date'], 'y': worldwide_grouped['Confirmed'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Confirmed Cases - Worldwide',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of people affected'},
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
                    {'x': worldwide_grouped['Date'], 'y': worldwide_grouped['Deaths'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Number of Deaths - Worldwide',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of people affected'},
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
                    {'x': worldwide_grouped['Date'], 'y': worldwide_grouped['Recovered'], 'type': 'line'},
                ],
                'layout': dict(
                    title='Recovered Cases - Worldwide',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Number of people affected'},
                )
            }
        )],
        style={'display': 'inline-block', 'width': '33%'}
    ),
	html.Div([
		dash_table.DataTable(
		    id='table',
		    columns=[{"name": i, "id": i} for i in summary_df[['Country', 'NewConfirmed', 'TotalConfirmed', 'NewDeaths', 'TotalDeaths', 'NewRecovered', 'TotalRecovered']].columns],
		    data=summary_df[['Country', 'NewConfirmed', 'TotalConfirmed', 'NewDeaths', 'TotalDeaths', 'NewRecovered', 'TotalRecovered']].to_dict('records'),
			style_cell={'padding': '5px', 'textAlign': 'left'},
		)],
		style={'width': '50%', 'padding-left': '10%', 'padding-right': '10%'}
	)
])

@app.callback(
    Output('confirmed-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_confirmed_graph (country_selected):
    dff = chart_data[chart_data['Country'] == country_selected]
    return {
        'data': [
            {'x': dff['Date'], 'y': dff['Confirmed'], 'type': 'line'},
        ],
        'layout': dict(
            title='Confirmed Cases - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of people affected'},
        )
    }

@app.callback(
    Output('deaths-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_confirmed_graph (country_selected):
    dff = chart_data[chart_data['Country'] == country_selected]
    return {
        'data': [
            {'x': dff['Date'], 'y': dff['Deaths'], 'type': 'line'},
        ],
        'layout': dict(
            title='Number of Deaths - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of people affected'},
        )
    }

@app.callback(
    Output('recovered-graph', 'figure'),
    [Input('country-selector', 'value')])
def update_confirmed_graph (country_selected):
    dff = chart_data[chart_data['Country'] == country_selected]
    return {
        'data': [
            {'x': dff['Date'], 'y': dff['Recovered'], 'type': 'line'},
        ],
        'layout': dict(
            title='Recovered Cases - '+ country_selected,
            xaxis={'title': 'Date'},
            yaxis={'title': 'Number of people affected'},
        )
            # 'title': 'Recovered Cases - ' + country_selected
    }

if __name__ == '__main__':
    app.run_server(debug=True)
