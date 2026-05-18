import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import yfinance as yf
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import os

email = os.getenv("VALID_EMAIL")
password = os.getenv("VALID_PASSWORD")

NIFTY_100_TICKERS = [
    # Nifty 50 Stocks
    "ADANIGREEN.NS", "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BHARTIARTL.NS",
    "BPCL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
    "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS",
    "HDFCBANK.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
    "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "OLECTRA.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBIN.NS", "SHREECEM.NS",
    "SUNPHARMA.NS", "TCS.NS", "TECHM.NS", "TITAN.NS","HDFCBANK.NS",
    "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS", "ZEEL.NS",

    # Additional Nifty 100 Stocks
    "AARTIIND.NS", "ALKEM.NS", "AMBUJACEM.NS", "ASAHIINDIA.NS",
    "BANDHANBNK.NS", "BIOCON.NS", "GAIL.NS", "HINDZINC.NS",
    "HDFCLIFE.NS", "ICICIGI.NS", "BAJAJHLDNG.NS", "TATASTEEL.NS",
    "LUPIN.NS", "LALPATHLAB.NS", "MARICO.NS", "INDUSINDBK.NS",
    "M&MFIN.NS", "PFC.NS", "GLENMARK.NS","IOC.NS",
    "CONCOR.NS", "GODREJCP.NS", "SBILIFE.NS",

    #Other Stocks
    "FORTIS.NS", "ANANTRAJ.NS", "ABB.NS","HAL.NS", "BEL.NS", "APOLLOHOSP.NS", 
    "HDFCAMC.NS", "DABUR.NS","ADANIENT.NS",

    # ETFs
    "NIFTYBEES.NS", "ITBEES.NS", "ALPHA.NS", "HDFCSML250.NS",
    "BANKBEES.NS", "MID150BEES.NS", "MON100.NS", "MASPTOP50.NS",
    "MAFANG.NS", "MONQ50.NS"
]

def run_lstm_prediction(close_data, prediction_days, look_back=60, epochs=25):
    np.random.seed(42)
    tf.random.set_seed(42)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_data.values.reshape(-1, 1))

    x_train, y_train = [], []
    for i in range(look_back, len(scaled_data)):
        x_train.append(scaled_data[i-look_back:i, 0])
        y_train.append(scaled_data[i, 0])
        
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.LSTM(units=50, return_sequences=False, input_shape=(x_train.shape[1], 1)))
    model.add(tf.keras.layers.Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(x_train, y_train, batch_size=32, epochs=epochs, verbose=0)

    future_predictions = []
    current_batch = scaled_data[-look_back:].reshape(1, look_back, 1)

    for _ in range(prediction_days):
        pred = model.predict(current_batch, verbose=0)[0]
        future_predictions.append(pred)
        current_batch = np.append(current_batch[:, 1:, :], [[pred]], axis=1)

    future_prices = scaler.inverse_transform(future_predictions)
    return future_prices.flatten()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Stock Analyzer"


login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("🔒 Secure Login", className="text-center text-primary mb-2"),
                    html.P("Enter your credentials to access the AI Wealth Manager.", className="text-center text-muted small mb-4"),
                    
                    dbc.Input(id="login-email", type="email", placeholder="Email Address", className="mb-3"),
                    dbc.Input(id="login-password", type="password", placeholder="Password", className="mb-4"),
                    
                    dbc.Button("Login to Dashboard", id="btn-login", color="primary", size="lg", className="w-100 mb-3"),
                    
                    html.Div(id="login-alert") 
                ])
            ], className="shadow-lg mt-5 border-0 rounded-lg")
        ], width=12, md=6, lg=4, className="mx-auto mt-5")
    ], className="vh-100 align-items-center")
], fluid=True, style={"backgroundColor": "#f8f9fa"})


dashboard_layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("🚀 Wealth Manager", className="text-center text-primary mb-2"), width=12),
        dbc.Col(html.P("Predict stocks, Manage Portfolio, & Find Swing Trades.", className="text-center text-muted"), width=12),
        html.Hr()
    ], className="mt-4"),

    dbc.Tabs([
        
        dbc.Tab(label="🔎 Single Stock Predictor", children=[
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Stock Symbol:"),
                            dbc.Input(id="input-ticker", placeholder="e.g. RELIANCE.NS", type="text", value="RELIANCE.NS"),
                        ], width=12, md=4),
                        
                        dbc.Col([
                            dbc.Label("Prediction Period:"),
                            dbc.Select(
                                id="input-months",
                                options=[
                                    {"label": "1 Month", "value": "1"},
                                    {"label": "3 Months", "value": "3"},
                                    {"label": "6 Months", "value": "6"},
                                    {"label": "1 Year", "value": "12"},
                                    {"label": "2 Years", "value": "24"},
                                ],
                                value="3"
                            ),
                        ], width=12, md=4),
                        
                        dbc.Col([
                            dbc.Label("Action:"),
                            dbc.Button("Run DL Prediction", id="btn-analyze", color="primary", className="w-100"),
                        ], width=12, md=4),
                    ], className="mb-4"),

                    dcc.Loading(
                        id="loading-single",
                        type="cube",
                        color="#2c3e50",
                        children=html.Div(id="single-stock-content")
                    ),
                ])
            ], className="mt-3 shadow-sm")
        ]),

        dbc.Tab(label="💼 Portfolio Analyzer", children=[
            dbc.Card([
                dbc.CardBody([
                    html.H5("Build Your Portfolio", className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Stock Ticker"), dbc.Input(id="pt-ticker", placeholder="e.g. TATASTEEL.NS", type="text")], width=4),
                        dbc.Col([dbc.Label("Buy Price (Avg)"), dbc.Input(id="pt-price", placeholder="e.g. 150", type="number")], width=3),
                        dbc.Col([dbc.Label("Quantity"), dbc.Input(id="pt-qty", placeholder="e.g. 100", type="number")], width=3),
                        dbc.Col([dbc.Label("Action"), dbc.Button("Add Stock", id="btn-add-stock", color="success", className="w-100")], width=2),
                    ], className="mb-4"),

                    html.Div([
                        dbc.Label("Your Watchlist:", className="text-muted small"),
                        dash_table.DataTable(
                            id='portfolio-table',
                            columns=[
                                {'name': 'Ticker', 'id': 'Ticker', 'type': 'text'},
                                {'name': 'Buy Price', 'id': 'Buy Price', 'type': 'numeric'},
                                {'name': 'Quantity', 'id': 'Quantity', 'type': 'numeric'},
                            ],
                            data=[], 
                            editable=True,        
                            row_deletable=True,    
                            style_cell={'textAlign': 'left', 'padding': '10px'},
                            style_header={'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': 'white'},
                        )
                    ], className="mb-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Project Growth For:"),
                            dbc.Select(
                                id="pt-months",
                                options=[
                                    {"label": "3 Months", "value": "3"},
                                    {"label": "6 Months", "value": "6"},
                                    {"label": "1 Year", "value": "12"},
                                ],
                                value="6"
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Analyze Full Portfolio (LSTM):"),
                            dbc.Button("🚀 Predict Portfolio Future", id="btn-calc-portfolio", color="primary", className="w-100"),
                        ], width=6),
                    ]),
                    dcc.Loading(
                        id="loading-portfolio",
                        type="dot",
                        color="#2c3e50",
                        children=html.Div(id="portfolio-results", className="mt-4")
                    ),
                ])
            ], className="mt-3 shadow-sm")
        ]),

        dbc.Tab(label="⚡ Swing Scanner", children=[
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H4("Hybrid AI Swing Finder", className="text-danger"),
                        html.P("Scans for AI-powered Buying dips and overextended Selling targets using pure RSI momentum.", className="text-muted"),
                    ], className="text-center mb-4"),
                    
                    dbc.Row([
                        dbc.Col(
                            dbc.Button("🛡️ Scan Markets", id="btn-scan", color="danger", size="lg", className="w-100"),
                            width={"size": 6, "offset": 3}
                        )
                    ]),

                    html.Hr(),

                    dcc.Loading(
                        id="loading-scanner",
                        type="default",
                        color="#e74c3c",
                        children=html.Div(id="scanner-content", className="mt-4")
                    )
                ])
            ], className="mt-3 shadow-sm")
        ])

    ]),

    dbc.Row([
        dbc.Col(html.Small("Developed By Rutvik | This Is Only For Education Purpose, Before Invest Do Your Own Reserch", className="text-muted"), className="text-center mt-5 mb-3")
    ])

], fluid=True)

app.layout = html.Div(id="page-content", children=login_layout)

@app.callback(
    Output("page-content", "children"),
    Output("login-alert", "children"),
    Input("btn-login", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def authenticate_user(n_clicks, email, password):
    if email == email and password == password:
        return dashboard_layout, dash.no_update
    else:
        error_msg = dbc.Alert("Incorrect Email or Password. Please try again.", color="danger", className="mt-3")
        return dash.no_update, error_msg


@app.callback(
    Output("single-stock-content", "children"),
    Input("btn-analyze", "n_clicks"),
    State("input-ticker", "value"),
    State("input-months", "value")
)
def update_single_stock(n_clicks, ticker, months):
    if not n_clicks: return html.Div()
    if not ticker: return dbc.Alert("Enter a ticker.", color="warning")

    try:
        prediction_days = int(months) * 30
        stock_symbol = ticker.strip().upper()
        
        df = yf.download(stock_symbol, period="max", progress=False, auto_adjust=True)
        if df.empty: return dbc.Alert(f"Data not found for {stock_symbol}", color="danger")
        
        close_data = df['Close']
        if isinstance(close_data, pd.DataFrame): close_data = close_data.iloc[:, 0]
        
        current_price = float(close_data.iloc[-1])
        
        last_date = df.index[-1]
        if last_date.tz is not None: last_date = last_date.tz_localize(None)
        
        future_dates = pd.date_range(start=last_date, periods=prediction_days + 1, freq='B')[1:]
        
        predicted_values = run_lstm_prediction(close_data, prediction_days)
        future_price = float(predicted_values[-1])

        x_actual = df.index[-500:].tolist() 
        y_actual = close_data.iloc[-500:].tolist()
        
        x_future = future_dates.tolist()
        y_future = predicted_values.tolist()
        
        x_future_connected = [x_actual[-1]] + x_future
        y_future_connected = [y_actual[-1]] + y_future

        price_diff = future_price - current_price
        pct_change = (price_diff / current_price) * 100
        color_class = "success" if price_diff >= 0 else "danger"
        
        fig_main = go.Figure()
        fig_main.add_trace(go.Scatter(x=x_actual, y=y_actual, name="Actual Price", line=dict(color="#2c3e50", width=2)))
        fig_main.add_trace(go.Scatter(x=x_future_connected, y=y_future_connected, name="LSTM Prediction", line=dict(color="#e74c3c", width=2, dash='dash')))
        
        fig_main.update_layout(
            title=f"Deep Learning Forecast: {stock_symbol}", 
            template="plotly_white", 
            margin=dict(t=40, b=20), 
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Price (₹)"
        )

        return html.Div([
            dbc.Alert([
                html.H4(f"Expected Return: {pct_change:.2f}%", className=f"text-{color_class}"),
                html.P(f"Price: ₹{current_price:.1f} → ₹{future_price:.1f}")
            ], color="light", className="mb-3 border"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_main), width=12)
            ]),
            html.P("Prediction powered by Long Short-Term Memory (LSTM) Neural Network.", className="text-center text-muted mt-3 small")
        ])
        
    except Exception as e:
        import traceback
        return dbc.Alert([html.P(str(e)), html.Pre(traceback.format_exc())], color="danger")


@app.callback(
    Output("portfolio-table", "data"),
    Input("btn-add-stock", "n_clicks"),
    State("pt-ticker", "value"),
    State("pt-price", "value"),
    State("pt-qty", "value"),
    State("portfolio-table", "data"),
    prevent_initial_call=True
)
def add_to_table(n_clicks, ticker, price, qty, existing_data):
    if not existing_data: existing_data = []
    if ticker and price and qty:
        new_row = {
            "Ticker": ticker.strip().upper(),
            "Buy Price": float(price),
            "Quantity": int(qty)
        }
        existing_data.append(new_row)
    return existing_data


@app.callback(
    Output("portfolio-results", "children"),
    Input("btn-calc-portfolio", "n_clicks"),
    State("portfolio-table", "data"),
    State("pt-months", "value"),
    prevent_initial_call=True
)
def analyze_portfolio(n_clicks, portfolio_data, months):
    if not portfolio_data:
        return dbc.Alert("Add stocks to table first.", color="warning")

    try:
        results = []
        total_current_value = 0
        total_future_value = 0
        prediction_days = int(months) * 30

        for stock in portfolio_data:
            if not stock.get('Ticker'): continue
            
            ticker = stock['Ticker']
            qty = float(stock['Quantity'])
            buy_price = float(stock['Buy Price'])  
            
            df = yf.download(ticker, period="max", progress=False, auto_adjust=True)
            if df.empty: continue
            
            close_data = df['Close']
            if isinstance(close_data, pd.DataFrame): close_data = close_data.iloc[:, 0]
            
            current_market_price = float(close_data.iloc[-1])
            
            predicted_values = run_lstm_prediction(close_data, prediction_days)
            future_market_price = float(predicted_values[-1])
            
            curr_val = current_market_price * qty
            fut_val = future_market_price * qty
            
            total_current_value += curr_val
            total_future_value += fut_val
            
            results.append({
                "Ticker": ticker,
                "Buy Price": round(buy_price, 2),
                "Current Price": round(current_market_price, 2),
                "Predicted Price": round(future_market_price, 2),
                "Current Value": round(curr_val, 2),
                "Future Value": round(fut_val, 2)
            })

        net_change = total_future_value - total_current_value
        net_pct = (net_change / total_current_value) * 100
        color = "success" if net_change > 0 else "danger"
        sign = "+" if net_change > 0 else ""
        
        summary_section = dbc.Row([
            dbc.Col(dbc.Alert([html.H5("Current Value"), html.H3(f"₹{total_current_value:,.0f}")], color="secondary"), width=4),
            dbc.Col(dbc.Alert([html.H5("Future Value"), html.H3(f"₹{total_future_value:,.0f}")], color="primary"), width=4),
            dbc.Col(dbc.Alert([html.H5("Net Profit"), html.H3(f"{sign}₹{net_change:,.0f} ({sign}{net_pct:.1f}%)")], color=color), width=4),
        ])

        df_res = pd.DataFrame(results)
        fig_pie = px.pie(df_res, values='Current Value', names='Ticker', title='Portfolio Weight Allocation', hole=0.3)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_res['Ticker'], y=df_res['Current Value'], name='Today', marker_color='#95a5a6'))
        fig_bar.add_trace(go.Bar(x=df_res['Ticker'], y=df_res['Future Value'], name='Future', marker_color='#2ecc71'))
        fig_bar.update_layout(barmode='group', title="Current vs Predicted Value (LSTM Engine)", template="plotly_white")

        detailed_table = dash_table.DataTable(
            data=df_res.to_dict('records'),
            columns=[
                {'name': 'Ticker', 'id': 'Ticker'},
                {'name': 'Buy Price', 'id': 'Buy Price'},
                {'name': 'Current Price', 'id': 'Current Price'},
                {'name': 'Predicted Price', 'id': 'Predicted Price'},
                {'name': 'Current Value', 'id': 'Current Value'},
                {'name': 'Future Value', 'id': 'Future Value'},
            ],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': 'white', 'border': '1px solid #eee'},
        )

        return html.Div([
            summary_section,
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_pie), width=12, lg=5),
                dbc.Col(dcc.Graph(figure=fig_bar), width=12, lg=7)
            ]),
            html.Hr(),
            html.H5("Detailed Price Breakdown", className="mt-4 mb-3 text-primary"),
            detailed_table,
            html.P("Portfolio predictions powered by Deep Learning (LSTM)", className="text-center text-muted mt-3 small")
        ])

    except Exception as e:
        import traceback
        return dbc.Alert([html.P(str(e)), html.Pre(traceback.format_exc())], color="danger")


@app.callback(
    Output("scanner-content", "children"),
    Input("btn-scan", "n_clicks"),
    prevent_initial_call=True
)
def scan_nifty_swing(n_clicks):
    try:
        data = yf.download(NIFTY_100_TICKERS, period="3y", group_by='ticker', threads=False, auto_adjust=True)
        
        buy_filtered_stocks = []
        sell_opportunities = []

        for ticker in NIFTY_100_TICKERS:
            try:
                df = data[ticker].copy()
                
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(0)
                
                df.dropna(inplace=True)
                if df.empty or len(df) < 200: continue

                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).fillna(0)
                loss = (-delta.where(delta < 0, 0)).fillna(0)

                avg_gain = gain.ewm(com=13, min_periods=14).mean()
                avg_loss = loss.ewm(com=13, min_periods=14).mean()
                
                rs = avg_gain / avg_loss
                df['RSI'] = 100 - (100 / (1 + rs))

                current_price = df['Close'].iloc[-1]
                current_rsi = df['RSI'].iloc[-1]

                if pd.isna(current_rsi):
                    continue
                
                if current_rsi <= 30:
                    buy_filtered_stocks.append({
                        "ticker": ticker,
                        "current_price": current_price,
                        "rsi": current_rsi,
                        "df": df
                    })
                
                if current_rsi >= 70:
                    sell_opportunities.append({
                        "Stock": ticker.replace(".NS", ""),
                        "Current Price": f"₹{current_price:.2f}",
                        "Signal": "Sell Future/Sell Call",
                        "RSI_raw": current_rsi 
                    })

            except Exception as e:
                continue

        buy_opportunities = []
        if buy_filtered_stocks:
            top_5_stocks = sorted(buy_filtered_stocks, key=lambda x: x['rsi'])[:5]
            
            for item in top_5_stocks:
                ticker = item['ticker']
                current_price = item['current_price']
                close_data = item['df']['Close']
                
                predicted_values = run_lstm_prediction(close_data, prediction_days=30, epochs=10)
                target_price = float(predicted_values[-1])
                pct_profit = ((target_price - current_price) / current_price) * 100
                
                buy_opportunities.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Current Price": f"₹{current_price:.2f}",
                    "AI Target (1M)": f"₹{target_price:.2f}",
                    "Expected Profit": f"{pct_profit:.2f}%"
                })
        
        if buy_opportunities:
            df_buy = pd.DataFrame(buy_opportunities)
            buy_tab_content = html.Div([
                dash_table.DataTable(
                    data=df_buy.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df_buy.columns],
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={'backgroundColor': '#27ae60', 'color': 'white', 'fontWeight': 'bold'},
                    style_data={'backgroundColor': 'white', 'border': '1px solid #eee'},
                )
            ])
        else:
            buy_tab_content = dbc.Alert("No AI Buying setups found today (No stocks with RSI <= 30).", color="info")

        if sell_opportunities:
            sell_opportunities = sorted(sell_opportunities, key=lambda x: x['RSI_raw'], reverse=True)
            for row in sell_opportunities:
                del row['RSI_raw']
                
            df_sell = pd.DataFrame(sell_opportunities)
            sell_tab_content = html.Div([
                dash_table.DataTable(
                    data=df_sell.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df_sell.columns],
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
                    style_data={'backgroundColor': 'white', 'border': '1px solid #eee'},
                )
            ])
        else:
            sell_tab_content = dbc.Alert("No overextended Selling setups found today (No stocks with RSI >= 70).", color="info")

        return dbc.Tabs([
            dbc.Tab(buy_tab_content, label=f"🟢 Buying ({len(buy_opportunities)})", className="mt-3"),
            dbc.Tab(sell_tab_content, label=f"🔴 Selling ({len(sell_opportunities)})", className="mt-3"),
        ])

    except Exception as e:
        import traceback
        return dbc.Alert([html.P(str(e)), html.Pre(traceback.format_exc())], color="danger")

if __name__ == '__main__':
    app.run(debug=True)