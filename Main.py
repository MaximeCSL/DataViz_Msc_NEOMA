#!/usr/bin/env python3
import dash
import theme
import plotly.io as pio
import plotly.graph_objects as go
from dash import html, dcc
import webbrowser
import threading
import datetime
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_table
import API
import Fetch_excel_ptf 
import warnings
import numpy as np
# Ignorer tous les warnings
warnings.filterwarnings('ignore')


EXCEL_FILE = 'Portfolio.xlsx'
sheet_name = 'Sheet1'

def calculate_rolling_sharpe_ratio(ptf_value, window=252, risk_free_rate=0.0):
    """
    Calculate the rolling annualized Sharpe Ratio based on portfolio values.
    
    Parameters:
    ptf_value (pd.Series): Series of portfolio values over time.
    window (int): Rolling window size in days, default is 252 (one trading year).
    risk_free_rate (float): Risk-free rate, default is 0.
    
    Returns:
    pd.Series: Rolling annualized Sharpe Ratio
    """
    # Calculate daily returns
    daily_returns = ptf_value.pct_change().dropna()
    
    # Calculate rolling annualized return
    rolling_annualized_return = ((1 + daily_returns.rolling(window).mean()) ** 252) - 1
    
    # Calculate rolling annualized volatility
    rolling_annualized_volatility = daily_returns.rolling(window).std() * np.sqrt(252)
    
    # Calculate rolling Sharpe Ratio
    rolling_sharpe_ratio = (rolling_annualized_return - risk_free_rate) / rolling_annualized_volatility
    
    return rolling_sharpe_ratio.dropna()
    
def calculate_var(returns, confidence_level=0.95):
    """
    Calculate the Value at Risk (VaR) for a series of returns.
    :param returns: A pandas Series of returns.
    :param confidence_level: The confidence level for VaR calculation.
    :return: The VaR value.
    """
    var = np.percentile(returns, (1 - confidence_level) * 100)
    return var

def process_main_data():

    fetcher = Fetch_excel_ptf.ExcelDataFetcher(EXCEL_FILE, sheet_name)
    transactions_data = fetcher.fetch_data()
    assets = list(transactions_data['ID'].unique())
    fetcher = API.AssetDataFetcher(assets)
    df = fetcher.fetch_data()
    quantities = pd.DataFrame(index=df.index,columns=df.columns)
    prices = pd.DataFrame(index=df.index,columns=df.columns)
    
    for _, row in transactions_data.iterrows():
        date = row[0]       # Première colonne (indice 0) pour la date
        asset = row[1]      # Deuxième colonne (indice 1) pour l'identifiant de l'actif
        quantity = row[2]   # Troisième colonne (indice 2) pour la quantité
        price = row[3]      # Quatrième colonne (indice 3) pour le prix
    
        quantities.at[date, asset] = quantity
        prices.at[date, asset] = price
    
    quantities.fillna(0, inplace=True)
    prices.fillna(0, inplace=True)
    
    buy_sell_price = pd.DataFrame(index=df.index)
    buy_sell_price['Cash']=-(quantities*prices).sum(axis=1)
    
    
    quantities_cum = quantities.cumsum()
    quantities_cum = quantities_cum.loc[~(quantities_cum == 0).all(axis=1)]
    
    ptf_asset_price = quantities_cum*df
    ptf_asset_price = ptf_asset_price.loc[~(ptf_asset_price == 0).all(axis=1)].dropna()
    
    
    ptf_value=ptf_asset_price.sum(axis=1)
    
    
    Pnl= buy_sell_price.sum() + ptf_value.iloc[-1]
    assets_return = df.pct_change().dropna()
    weights = ptf_asset_price.div(ptf_asset_price.sum(axis=1), axis=0)
    weighted_return = (weights*assets_return).dropna().sum(axis=1)
    ptf_cum_return = (1+weighted_return).cumprod()-1
    var = calculate_var(weighted_return)

    return ptf_cum_return,weighted_return,Pnl,ptf_value,ptf_asset_price,quantities_cum,buy_sell_price, var



pio.templates.default = theme.theme


# URL to the external CSS file (Bootswatch Pulse theme)
external_stylesheets = ['https://bootswatch.com/5/pulse/bootstrap.min.css']
EXCEL_FILE = '/Users/casalino/Desktop/Analyses_portfolio/Portfolio.xlsx'
df = pd.read_excel(EXCEL_FILE)

# Initialize the Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
today = datetime.date.today()
app.layout = html.Div([
    html.Div(className='row', style={'height': '40px'}),                
        html.Div([
        html.H1("Personal portfolio analysis", style={'color': theme.purple, 'textAlign': 'center', 'marginBottom': '10px'}),
        html.Div([
            html.P("Linkedin profil", style={'marginRight': '20px', 'fontWeight': 'bold'}),
            html.A("Maxime CASALINO", href="https://www.linkedin.com/in/maxime-casalino-96babb178/", target="_blank"),
            html.Div(className='row', style={'height': '10px'}),   
            html.A("Nicolas RUIZ", href="https://www.linkedin.com/in/nicolas--ruiz/", target="_blank"),
            html.Img(src='/assets/ecole.png', style={'position': 'absolute', 'top': '20px', 'right': '10px', 'height': '80px'})
        ]),
            

            html.Button('Show/hide Table', id='toggle-table-button', n_clicks=0, 
                        style={'backgroundColor': theme.purple, 'color': 'white', 'borderRadius': '5px', 'marginTop': '00px'}),
            html.Div(
                id='table-container',
                children=[
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        editable=True,
                        row_deletable=True,
                        style_cell={'textAlign': 'center'},
                        sort_action='native',
                        filter_action='native',
                        page_action='native',
                        page_size=10
                    )
                ],
                style={'display': 'block'}  # Initially hide the table
            ),
            html.Div([
                dcc.DatePickerSingle(
                    id='date-picker-single',
                    max_date_allowed=today,
                    date=today,
                    style={'marginRight': '20px'}
                ),
                html.Button('Add Rows', id='editing-rows-button', n_clicks=0, 
                            style={'backgroundColor': theme.purple, 'color': 'white', 'borderRadius': '5px', 'marginLeft': '20px', 'marginRight': '20px'}),
                html.Button('Save', id='save-button', n_clicks=0, 
                            style={'backgroundColor': theme.purple, 'color': 'white', 'borderRadius': '5px', 'marginLeft': '20px', 'marginRight': '20px'}),
                html.Button("Run", id="run-button", 
                            style={'backgroundColor': theme.purple, 'color': 'white', 'borderRadius': '5px', 'marginLeft': '20px'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),
            html.Div(id='save-message', style={'textAlign': 'center', 'marginTop': '10px'})

            
        ], style={'padding': '20px'}),
                                                
                                


    # Ligne vide pour l'espacement
    html.Div(className='row', style={'height': '40px'}),

    # Première ligne avec deux graphiques et leurs titres
    html.Div(className='row', children=[
        html.Div([
            html.H4("Cumulative return", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph1')
        ], className='col-6'),
        html.Div([
            html.H4("Portfolio value", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph2')
        ], className='col-6'),
    ]),
    
    html.Div(className='row', children=[
        html.Div([
            html.H4("Returns", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph3')
        ], className='col-6'),
        html.Div([
            html.H4("Value per asset", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph4')
        ], className='col-6'),
    ]),
    
    html.Div(className='row', children=[
        html.Div([
            html.H4("Performances (%)", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph5')
        ], className='col-6'),
        html.Div([
            html.H4("PnL as of yesterday", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph6')
        ], className='col-6'),
    ]),
    
    html.Div(className='row', children=[
        html.Div([
            html.H4("Quantities of each stocks", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph7')
        ], className='col-6'),
        html.Div([
            html.H4("Ptf repartition", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph8')
        ], className='col-6'),
    ]),
    
    html.Div(className='row', children=[
        html.Div([
            html.H4("Cash out by period", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph9')
        ], className='col-6'),
        html.Div([
            html.H4("Annualized Return adjusted", style={'textAlign': 'center', 'color': theme.purple}),
            dcc.Graph(id='graph10')
        ], className='col-6'),
    ]),

])



@app.callback(
    [
        Output('graph1', 'figure'),
        Output('graph2', 'figure'),
        Output('graph3', 'figure'),
        Output('graph4', 'figure'),
        Output('graph5', 'figure'),
        Output('graph6', 'figure'),
        Output('graph7', 'figure'),
        Output('graph8', 'figure'),
        Output('graph9', 'figure'),
        Output('graph10', 'figure'),

    ],
    [State('date-picker-single', 'date'),
     Input("run-button", "n_clicks")],
    prevent_initial_call=True
)


def update_all_graphs(selected_date,n_clicks):
    if n_clicks:
        
        Main_data = process_main_data()
        # Create figures for each graph
        fig1 = px.line(Main_data[0][Main_data[0].index <= selected_date])
        fig1.update_layout(showlegend=False)  
        fig1.update_yaxes(title=None)  
        fig1.update_xaxes(title=None) 
        
        
        
        fig2 = px.line(Main_data[3][Main_data[3].index <= selected_date])
        fig2.update_layout(showlegend=False)  
        fig2.update_yaxes(title=None) 
        fig2.update_xaxes(title=None)  
        
         
        fig3 = px.line(Main_data[1][Main_data[1].index <= selected_date])
        fig3.update_layout(showlegend=True)  
        fig3.update_yaxes(title=None) 
        fig3.update_xaxes(title=None) 
        var=calculate_var(Main_data[1])
        fig3.add_hline(y=Main_data[7], line=dict(color=theme.blue, width=2), name='VaR (95%)')

        
        fig4 = px.line(Main_data[4][Main_data[4].index <= selected_date])
        fig4.update_yaxes(title=None) 
        fig4.update_xaxes(title=None)  

        
        list_dates = Main_data[0][Main_data[0].index <= selected_date].index
        
        
        today = pd.to_datetime(selected_date)
        start_of_year = today.replace(month=1, day=1)
        one_year_ago = today - pd.DateOffset(years=1)
        one_month_ago = today - pd.DateOffset(months=1)
        start_of_data = Main_data[0].index[0]
    
        # Fonction pour trouver la valeur la plus proche pour une date donnée
        def get_closest_value(date):
            # Trouver l'index où la date donnée devrait être insérée
            idx = list_dates.searchsorted(date)
            
            # Gérer les cas où idx est à l'extrémité de l'index
            if idx == 0:
                return Main_data[0].iloc[0]
            if idx == len(list_dates):
                return Main_data[0].iloc[-1]
        
            # Prendre la date la plus proche avant ou après la date donnée
            prev_date = list_dates[idx - 1]
            next_date = list_dates[min(idx, len(list_dates) - 1)]
            
            # Choisir la date la plus proche de la date donnée
            if abs(date - next_date) < abs(date - prev_date):
                return Main_data[0][next_date]
            
            else:
                
                return Main_data[0][prev_date]
            
        # Calcul des performances en utilisant les dates les plus proches
        ytd_perf = (get_closest_value(today) - get_closest_value(start_of_year))
        one_year_perf = (get_closest_value(today) - get_closest_value(one_year_ago)) 
        one_month_perf = (get_closest_value(today) - get_closest_value(one_month_ago))
        since_inception_perf= (get_closest_value(today) - Main_data[0][Main_data[0].index <= selected_date].loc[list_dates[0]])
        # Création du graphique à barres pour fig5
        perf_data = {
            'Period': ['1 Month', 'YTD', '1 Year', 'Since Inception'],
            'Performance': [one_month_perf, ytd_perf, one_year_perf, since_inception_perf]
        }
        fig5 = px.bar(perf_data, x='Period', y='Performance')
        fig5.update_yaxes(title=None) 
    
        fig6 = go.Figure()
        fig6 = px.bar(Main_data[2])
        fig6.update_layout(showlegend=False)  
        fig6.update_yaxes(title=None) 
        fig6.update_xaxes(title=None)  
        
        fig7= px.bar(Main_data[5].iloc[-1])
        fig7.update_layout(showlegend=False)
        fig7.update_yaxes(title=None) 
        
        df_pie= Main_data[4].iloc[-1]*Main_data[5].iloc[-1]
        fig8 = px.pie(df_pie,names=df_pie.index,values=df_pie.values)
        fig8.update_layout(showlegend=False)
        fig8.update_yaxes(title=None) 
    
        fig9 = px.line(Main_data[6]['Cash'].cumsum())
        fig9.update_layout(showlegend=False)
        fig9.update_yaxes(title=None) 
        

        s_r = calculate_rolling_sharpe_ratio(Main_data[3])
        mean_return_adjusted=s_r.mean()
        fig10 = px.line(s_r)
        fig10.add_hline(y=mean_return_adjusted, line=dict(color=theme.blue, width=2), name='Mean Return Adjusted')
        fig10.update_yaxes(title=None) 
        fig10.update_layout(showlegend=False) 
        
        return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10
    
@app.callback(
    Output('table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table', 'data'),
    State('table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# Callback pour sauvegarder les modifications
@app.callback(
    Output('save-message', 'children'),
    Input('save-button', 'n_clicks'),
    State('table', 'data'))
def save_changes(n_clicks, rows):
    if n_clicks > 0:
        new_df = pd.DataFrame(rows)
        new_df.to_excel(EXCEL_FILE, index=False)
        return 'Saved !'
    
# Callback for toggling the table's visibility
@app.callback(
    Output('table-container', 'style'),
    [Input('toggle-table-button', 'n_clicks')],
    [State('table-container', 'style')]
)
def toggle_table(n_clicks, style):
    if n_clicks % 2 == 0:  # If n_clicks is even, hide the table
        style['display'] = 'block'
    else:  # If n_clicks is odd, show the table
        style['display'] = 'none'
    return style

def open_browser():
      webbrowser.open_new("http://127.0.0.1:8050/")

# Run the app
if __name__ == '__main__':
    # Use threading to open the web browser
    threading.Timer(1, open_browser).start()
    app.run_server(debug=True)
