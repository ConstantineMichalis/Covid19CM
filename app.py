import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import flask
import dash; import dash_core_components as dcc; import dash_html_components as html
from dash.dependencies import Input, Output

data = pd.read_csv('./OxCGRT_summary20200520.csv', sep= ',')
countries = pd.read_csv('./country-and-continent.csv', sep= ',')

data = data.rename(columns = {'School closing':'Schoolclosing', 'Stay at home requirements':'Stay_at_home_requirements'})

data['FullDate'] = list(map(lambda x: datetime.datetime.strptime(x,'%d/%m/%Y').strftime('%b/%d'), data.Date.astype(str)))
data['Day'] = list(map(lambda x: datetime.datetime.strptime(x,'%d/%m/%Y').strftime('%d'), data.Date.astype(str)))
data['Month'] = list(map(lambda x: datetime.datetime.strptime(x,'%d/%m/%Y').strftime('%m'), data.Date.astype(str)))


########################################################################################################
### Question 1
df = data.merge(countries, how='left', on=['CountryCode'])
null = df[df.Continent_Name.isnull()] #Kosovo not in file
df.loc[df['CountryCode'] == 'RKS', 'Continent_Name'] = 'Europe'
      
###############################################################################################################################
### Question 2
df.isnull().sum() # Confirmed cases and deaths null
data = df.dropna()
df =  df.sort_values(["CountryCode","Month", "Day"]).reset_index(drop=True) 

## Replace missing values with values of previous day for each country
#For Cases
for country in df.CountryCode.unique():
    for index, row in df.query("CountryCode == '"+country+"'").iterrows(): 
        if ((index == 0) and (np.isnan(df['ConfirmedCases'][index]))):
            df['ConfirmedCases'][index] = 0
        elif ((index != 0) and (df['CountryCode'][index] != df['CountryCode'][index-1]) and (np.isnan(df['ConfirmedCases'][index]))):
            df['ConfirmedCases'][index] = 0
        elif ((index != 0) and (df['CountryCode'][index] == df['CountryCode'][index-1]) and (np.isnan(df['ConfirmedCases'][index]))):
            df['ConfirmedCases'][index] = df['ConfirmedCases'][index - 1]
       
#For Deaths
for country in df.CountryCode.unique():
    for index, row in df.query("CountryCode == '"+country+"'").iterrows(): 
        if ((index == 0) and (np.isnan(df['ConfirmedDeaths'][index]))):
            df['ConfirmedDeaths'][index] = 0
        elif ((index != 0) and (df['CountryCode'][index] != df['CountryCode'][index-1]) and (np.isnan(df['ConfirmedDeaths'][index]))):
            df['ConfirmedDeaths'][index] = 0
        elif ((index != 0) and (df['CountryCode'][index] == df['CountryCode'][index-1]) and (np.isnan(df['ConfirmedDeaths'][index]))):
            df['ConfirmedDeaths'][index] = df['ConfirmedDeaths'][index - 1]
   


dftop = df.query("Date == '30/12/2021'").groupby(['CountryCode', 'FullDate', 'Date'])[['ConfirmedCases', 'StringencyIndex', 'ConfirmedDeaths']].mean().reset_index()
dftop = dftop.sort_values(by=['ConfirmedCases'], ascending=False).head(5)


#Question 5)b)
mycols = ['#e4717a', '#5d8aa8', '#a4c639', '#ffa812', '#a67b5b', '#915c83']

server = flask.Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

fig = px.scatter_geo(df, locations="CountryCode", color="Continent_Name", 
                     size="ConfirmedCases", scope = "world",size_max=80, animation_frame="Date", 
                     title = "ConfirmedCases Globally", projection="equirectangular")


fig2 = px.line(df[df['CountryCode'].isin(dftop['CountryCode'])], x="FullDate", y="ConfirmedCases",
               color='CountryCode', color_discrete_sequence   = mycols, 
               title = "ConfirmedCases in the top five countries", log_y=True,)


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([html.Label('Multi-Select Dropdown'), 
                  dcc.Dropdown(id = "Scope", options=[{'label': 'World', 'value': 'all'},
                                                      {'label': 'Asia', 'value': 'asia'},
                                                      {'label': 'Africa', 'value': 'africa'},
                                                      {'label': 'Europe', 'value': 'europe'},
                                                      {'label': 'North America', 'value': 'north america'},
                                                      {'label': 'South America', 'value': 'south america'}], value='all'),
                  html.Br(),html.Br(),html.Label("Input Data"),
                  dcc.RadioItems(id="Data Input", options=[{'label': 'Confirmed Cases', 'value': 'ConfirmedCases'},
                                                           {'label': 'Stringency Index', 'value': 'StringencyIndex'},
                                                           {'label': 'Confirmed Deaths', 'value': 'ConfirmedDeaths'}], value='ConfirmedCases')], 
                      className="three columns"),
        html.Div([dcc.Graph(id="fig2", figure=fig2)], className="nine columns")
        ], className="row"),
    html.Div([dcc.Graph(id="fig1", figure=fig)], className="twelve columns")
        ], className="row")
    ])
        

@app.callback([Output('fig1', 'figure'), Output('fig2', 'figure')],[Input('Scope', 'value'),Input('Data Input', 'value')])
def updatefig(g,d):
    if g=="all" and d=="ConfirmedCases": return fig, fig2
    elif g=="all" and d!="ConfirmedCases": return  px.scatter_geo(df, locations="CountryCode", color="Continent_Name", scope = "world", size=d, size_max=20, title = d+" Globally", animation_frame="Date", projection="equirectangular"), px.line(df[df['CountryCode'].isin(dftop['CountryCode'])], x="FullDate", y=d,color='CountryCode', color_discrete_sequence   = mycols, title = d+" in the top five countries")
    elif g!="all" and d!="ConfirmedCases": return  px.scatter_geo(df, locations="CountryCode", color="Continent_Name", scope = g, size=d, size_max=20, title = d+" in "+g, animation_frame="Date", projection="equirectangular"), px.line(df[df['CountryCode'].isin(dftop['CountryCode'])], x="FullDate", y=d,color='CountryCode', color_discrete_sequence   = mycols, title = d+" in the top five countries")
    else: return  px.scatter_geo(df, locations="CountryCode", color="Continent_Name", scope = g, size='ConfirmedCases', size_max=80, title = d+" in "+g, animation_frame="Date", projection="equirectangular"), fig2

app.run_server(debug=True, use_reloader=False)

# Run the Dash app
if __name__ == "__main__":
    # Starting flask server
    app.run_server(debug=True)
