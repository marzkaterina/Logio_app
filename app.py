# -*- coding: utf-8 -*-

'''
dash
dash_bootstrap_templates
Plzen - Prerov      381 km
Prerov - Ostrava    83 km
Ostrava - Plzen     463 km
ZP10 Plzen
ZP20 Prerov
ZP30 Ostrava
'''

import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
from dash import Dash, dash_table, Input, Output, html, dcc, callback, State
import dash_bootstrap_components as dbc
import datetime 
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
### --------------------------------------------------------------------------
def read_data(file):
    '''
    Reads data from current path given file name.

    Parameters
    ----------
    file : str
        File name, e.g. 'dodavatele.csv'.

    Returns
    -------
    data : pd.DataFrame()
        Loaded data.

    '''
    ### - merge path
    #path = os.path.join(Path.cwd(), file)
    path = Path(__file__).parent / file
    
    ## - load data using ';' as separator

    data = pd.read_csv(path, sep = ';')
    
    ### - if data are loaded in single column
    if data.shape[1]<2:
        ### - load data using '\t' separator
        data = pd.read_csv(path, sep = '\t')
    return data

### - load datasets given file name
dodavatele = read_data('dodavatele.csv')
dodavky = read_data('dodavky.csv')
komponenty = read_data('komponenty.csv')
pohyby = read_data('pohyby.csv')
produkty = read_data('produkty.csv')
sklady = read_data('sklady.csv')
stav_skladu = read_data('stav_skladu_08_2018.csv')
zavody = read_data('zavody.csv')
matice_vyroby = read_data('matice_vyroby.txt')
vyroba = read_data('vyroba.txt')

def get_product_price(produkty, matice_vyroby, komponenty):
    '''
    Returns manufacturing cost of poroducts. Gets components of products and 
    their prices and returns an aggretate prices of products.

    Parameters
    ----------
    produkty : pd.DataFrame()
        Dataframe containing products and retail prices.
    matice_vyroby : pd.DataFrame()
        Dataframe containing products and corresponding components and 
        requested amount.
    komponenty : pd.DataFrame()
        Dataframe containing components and their prices.

    Returns
    -------
    produkty_all : pd.DataFrame()
        Dataframe containing products, retail prices and manufacture costs.

    '''
    produkty_all = produkty.copy()
    ### - extend by 'Vyrobni cena' column containing zeros
    produkty_all['Vyrobni_cena'] = np.zeros(len(produkty))
    for produkt in produkty['ID_produktu']:
        ### - product consists of N components, from matice_vyroby.txt
        mv_temp = matice_vyroby.loc[matice_vyroby['ID_produktu']==produkt, :]
        mv_temp.reset_index(drop = True, inplace = True)
        ### - price of a single component, from komponenty.csv
        p = 0
        for i in range(len(mv_temp)):
            ### - corresponding component
            komponenta = mv_temp.loc[i, 'ID_komponenty']
            ### - corresponding amount
            N = mv_temp.loc[i, 'Mnozstvi']
            ### - corresponding price
            p_temp = int(komponenty.loc[komponenty['ID_komponenty'] == komponenta, 
                                        'Porizovaci_cena'].to_numpy())
            p += p_temp * N
        
        produkty_all.loc[produkty_all['ID_produktu'] == produkt, 'Vyrobni_cena'] = p
    return produkty_all

produkty_all = get_product_price(produkty, matice_vyroby, komponenty)

def get_production_costs(produkty_all, vyroba):
    '''
    Returns manufacturing cost for manufactured products. 

    Parameters
    ----------
    produkty_all : pd.DataFrame()
        Dataframe containing products, retail prices and manufacture costs.
    vyroba : pd.DataFrame()
        Dataframe containing product, plant, date and manufactured amount.

    Returns
    -------
    produkty_all : pd.DataFrame()
        Dataframe containing product, plant, date and manufactured amount and
        manufacturing cost.

    '''
    vyroba_all = vyroba.copy()
    ### - 'Datum' as pd.Datetime (without time)
    vyroba_all['Datum']=pd.to_datetime(vyroba_all['Datum'], dayfirst = True).dt.date
    vyroba_all['Vyrobni_naklady'] = np.zeros(len(vyroba))
    for i in range(len(vyroba_all)):
        ### - get product ID from line i
        product_temp = vyroba_all.loc[i, 'ID_produktu']
        ### - get product price from produkty_all
        p = int(produkty_all.loc[produkty_all['ID_produktu'] == product_temp, 'Vyrobni_cena'].to_numpy())
        ### - get amount of manufactured products
        N = vyroba_all.loc[i, 'Mnozstvi']
        ### - append cost for manufactured products
        vyroba_all.loc[i, 'Vyrobni_naklady'] = float(p*N)
        
    return vyroba_all[['Datum', 'ID_produktu', 'ID_zavodu', 'Mnozstvi', 'Vyrobni_naklady']]
    
vyroba_all =  get_production_costs(produkty_all, vyroba)

def get_transport(pohyby):
    '''
    Returns distance between plants for components transport.

    Parameters
    ----------
    pohyby : pd.DataFrame()
        Dataframe containing start plant, target plant, date, transported weight.

    Returns
    -------
    pohyby_all : pd.DataFrame()
        Dataframe containing start plant, target plant, date, transported weight
        and distance between plants.

    '''
    pohyby_all = pohyby.copy()
    ### - add empty column for distances
    pohyby_all['Vzdalenost'] = np.zeros(len(pohyby))
    def distance(x, y):
        ### - returns approx. distance between plants
        if (x == 'ZP10' and y == 'ZP20') or (y == 'ZP10' and x == 'ZP20'):
            return 381
        elif (x == 'ZP30' and y == 'ZP20') or (y == 'ZP30' and x == 'ZP20'):
            return 83
        elif (x == 'ZP10' and y == 'ZP30') or (y == 'ZP10' and x == 'ZP30'):
            return 463
    
    ### - add corresponding distance between plants in row
    for i in range(len(pohyby_all)):
        pohyby_all.loc[i, 'Vzdalenost'] = distance(pohyby_all.loc[i, 'ID_zavodu_vychozi'], 
                                                   pohyby_all.loc[i, 'ID_zavodu_cilove'])
        
    return pohyby_all

pohyby_all = get_transport(pohyby)
        
###---------------------------------------------------------------------------
### - initiate dash application usin externa theme
# MORPH, DARKLY, SLATE
app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH])
server = app.server

### - define sidebar with inputs
sidebar = html.Div(
    [
        html.H5("Filtry"), # title of sidebar
        html.Hr(),
        dbc.Nav(
            [
                html.Header("Vyberte časové období"),
                dcc.DatePickerRange(
                    display_format='D/M/YYYY', 
                    min_date_allowed=vyroba_all['Datum'].min(), 
                    max_date_allowed=vyroba_all['Datum'].max(),
                    start_date_placeholder_text="Začátek",
                    end_date_placeholder_text="Konec",
                    start_date=vyroba_all['Datum'].min(),
                    id='date-picker'
                ),
                html.Br(),
                html.Header('Vyberte výrobní závod'),
                dcc.Dropdown(
                    id='dd1',
                    options=[
                        {'label': 'ZP10', 'value': 'ZP10'},
                        {'label': 'ZP20', 'value': 'ZP20'},
                        {'label': 'ZP30', 'value': 'ZP30'}
                    ],
                    value='ZP10'
                ),
                html.Br(),
                html.Header("Zadejte cenu za km"),
                dcc.Input(
                    id="km-cost", type="number")
            ],
            vertical=True,
            pills=True,
        ),
    ]
)

### - define app layout
app.layout = html.Div(children=[
    dcc.Store(id='temp_data', data=vyroba_all.to_json(date_format='iso')),  
    dbc.Row(html.H1('Logio app')),
    dbc.Row(children = [
        dbc.Col(sidebar, width = 3),
        dbc.Col(children = [
            dbc.Row(
                dash_table.DataTable(id='table',
                                     columns=[{"name": i, "id": i} for i in (vyroba_all.columns)],
                                     page_size=10)
            ),
            dbc.Row(children = [
                dbc.Col(
                    dcc.Graph(id='graph-production'),
                    width = 6),
                dbc.Col(
                    dcc.Graph(id='graph-transport'),
                    width = 6)
                ]
                
            )],
            width = 8), ])
])

@app.callback(
    Output('temp_data', 'data'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')],
    prevent_initial_call=True
)
def filter_production_table(start_date, end_date):
    '''
    Returns filtered dataframe based on selected date range by 
    dcc.DatePickerRange and stores it in dcc.Store.

    Parameters
    ----------
    start_date : date
        Start date.
    end_date : date
        End date.

    Returns
    -------
    json
        Serialized dataframe containing only records from specified date range.

    '''
    ### - transform to strptime format
    sd = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ed = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    ### - select records from spedified date range and sort in ascending order
    temp_1 = vyroba_all.loc[vyroba_all['Datum'] >= sd, :]
    temp_2 = temp_1.loc[temp_1['Datum'] <= ed, :]
    temp_2.sort_values(by='Datum', inplace=True)
    return temp_2.to_json(date_format='iso', orient='split')  # Serialize DataFrame and store it in dcc.Store

@app.callback(
    Output('table', 'data'),
    [Input('temp_data', 'data')],
    prevent_initial_call=True
)
def update_table(json_data):
    '''
    Takes data from dcc.Store and sends them into dash_table.DataTabl.

    Parameters
    ----------
    json_data : json
        Serialized dataframe.

    Returns
    -------
    list of arrays
        Serialized dataframe.

    '''
    df = pd.read_json(json_data, orient='split')  # Deserialize the data back to a DataFrame
    df['Datum']=pd.to_datetime(df['Datum'], dayfirst = True).dt.date
    return df.to_dict('records')  # Return data as a list of records (rows)

@app.callback(
    Output('graph-production', 'figure'),
    [Input('dd1', 'value'),
     Input('temp_data', 'data')],
    prevent_initial_call=True
)
def update_bar_chart(plant, json_data):
    '''
    Takes data from dcc.Store and dcc.Dropdown and creates a bar plot.

    Parameters
    ----------
    plant : str
        Requested plant ID.
    json_data : json
        Serialized dataframe.

    Returns
    -------
    fig : fig object
        Barplot.

    '''
    df = pd.read_json(json_data, orient='split')  # Deserialize the data back to a DataFrame
    ### - filter dataset by plant ID from dcc.Dropdown
    df_temp = df[df['ID_zavodu'] == plant]
    ### - set figure and create barplot
    fig = go.Figure(data=[
        go.Bar(x=df_temp['ID_produktu'], y=df_temp['Mnozstvi'])])
    fig.update_layout(
        title={
        'text': 'Produkty vyrobené v '+str(plant),
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig

@app.callback(
    Output('graph-transport', 'figure'),
    [Input('dd1', 'value'),
     Input('km-cost', 'value')],
    [State('date-picker', 'start_date'),
     State('date-picker', 'end_date')],
    prevent_initial_call=True
)
def update_transport_chart(plant, cost, start_date, end_date):
    '''
    Takes data from dcc.Store, dcc.Dropdown and dcc.Input and creates a bar plot.

    Parameters
    ----------
    plant : str
        Requested plant ID.
    cost : int
        Estimated cost per km.
    start_date : date
        Start date.
    end_date : date
        End date.

    Returns
    -------
    fig : fig object
        Barplot.

    '''
    df = pohyby_all.copy()
    df['Datum'] = pd.to_datetime(df['Datum'], dayfirst = True).dt.date
    
    if start_date is None or end_date is None:
    ### - If no date is selected yet, return an empty figure
        return go.Figure()
    
    ### - transform to strptime format
    sd = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ed = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    ### - select records from spedified date range and sort in ascending order
    df = df.loc[df['Datum'] >= sd, :]
    df = df.loc[df['Datum'] <= ed, :]
    df.sort_values(by='Datum', inplace=True)
    
    ### - filter dataset by plant ID from dcc.Dropdown
    df_temp = df.loc[df['ID_zavodu_cilove'] == plant, :]
    ### - set figure and create barplot
    fig = go.Figure(data=[
        go.Bar(name='přepravená hmotnost [kg]', x=df_temp['ID_zavodu_vychozi'], y=df_temp['Objem_v_kg']),
        go.Bar(name='odhadovaná cena přepravy [czk]', x=df_temp['ID_zavodu_vychozi'], y=df_temp['Vzdalenost'] * float(cost))
    ])
    # Change the bar mode
    fig.update_layout(barmode='group',
                      title={
                      'text': 'Dovoz komponent do '+str(plant),
                      'y':0.9,
                      'x':0.5,
                      'xanchor': 'center',
                      'yanchor': 'top'})

    return fig
    
if __name__ == "__main__":
    app.run_server(debug=True)
