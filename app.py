import pandas as pd
import plotly.express as px
import flask
import dash; import dash_core_components as dcc; import dash_html_components as html
from dash.dependencies import Input, Output

# Setup the app. The server & app names should match those in Procfile 
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Associating server
server = app.server


dts = pd.read_csv('./Locationregions.csv', sep= ',',encoding='cp1252')
lab = pd.read_csv('./laborregions.csv', sep= ',',encoding='cp1252')

dts = dts[dts['PLUSPCUSTOMER'] != 'C1000238']
dts.dtypes
dts.ANCESTOR = dts.ANCESTOR.astype('object') 
dts.BRANCH = dts.BRANCH.astype('object') 
dts.TYPE = dts.TYPE.astype('object') 
lab.LOCATION = lab.LOCATION.astype('object') 
token = open("./mapbox.token").read()



mycols = ['#e4717a', '#5d8aa8', '#a4c639', '#ffa812', '#a67b5b', '#915c83']

dark = dts[dts['STATUS'] == 'OPERATING']
fig1 = px.scatter_mapbox(dark, lat="LATITUDEY", 
                        lon="LONGITUDEX",
                        color="ANCESTOR", hover_data=(['LOCATION', 'PLUSPCUSTOMER'])
                        #, animation_frame = "ANCESTOR"
                        )

fig1.update_layout(mapbox_center_lat=53.55, mapbox_center_lon=-2.433,
                  mapbox = {'accesstoken': token,  'style': "carto-darkmatter", 'zoom': 4.7})


app.title = 'Integral Regions'
app.layout = html.Div([
    html.Div([html.Label('Add Customer (Write "All" for full overview)'),
              dcc.Input(id = 'cust1', value = 'All', type = 'text')], className = 'three columns'),
    html.Div([dcc.Graph(id='fig1', figure=fig1,style={'height': '90vh'})], className="nine columns")])

@app.callback (Output('fig1', 'figure'), [Input('cust1', 'value')])
def updatefig(g):
    if g=="All": return fig1
    elif g=="all": return fig1
    else: return px.scatter_mapbox(dark.query("PLUSPCUSTOMER == '"+g+"'"), lat="LATITUDEY", lon="LONGITUDEX", color="ANCESTOR", hover_data=(['LOCATION', 'PLUSPCUSTOMER'])).update_layout(mapbox_center_lat=53.55, mapbox_center_lon=-2.433, mapbox = {'accesstoken': token,  'style': "carto-darkmatter", 'zoom': 4.7})


# Run the Dash app
if __name__ == "__main__":
    # Starting flask server
    app.run_server(debug=True)
