import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

from config import COLORS_BASE_THEME, CATEGORIES

from statsmodels.tsa.stattools import adfuller, kpss


def print_stat_card(column, header, value):
    with column:
        st.write(header)
        st.write(value)


def print_main_chart(data):
    fig = go.Figure()

    for company in data.columns:
        fig.add_trace(
            go.Scatter(
                x = data.index,
                y = data[company],
                mode = 'lines',
                name = company,
                line = {
                    'color': COLORS_BASE_THEME['categories'][CATEGORIES[company]],
                    'width': 2
                }
            )
        )

    fig.update_layout(
        title = {
            'text': 'Цена закрытия',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Цена ($)',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    return fig


def print_returns_chart(data):
    fig = go.Figure()

    for company in data.columns:
        fig.add_trace(
            go.Bar(
                x = data.index,
                y = data[company],
                name = company,
                marker = {
                    'color': COLORS_BASE_THEME['categories'][CATEGORIES[company]]
                },
                orientation = 'v'
            )
        )

    fig.update_layout(
        title = {
            'text': 'Доходности',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Доходности (%)',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    return fig  


def print_volatility_chart(data):
    fig = go.Figure()

    for company in data.columns:
        fig.add_trace(
            go.Scatter(
                x = data.index,
                y = data[company],
                mode = 'lines',
                fill = 'tozeroy',
                name = company,
                line = {
                    'color': COLORS_BASE_THEME['categories'][CATEGORIES[company]],
                    'width': 2
                }
            )
        )

    fig.update_layout(
        title = {
            'text': 'Волатильность',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Волатильность',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    return fig 


def get_statistic_coefs(data, type):

    kpss_types = {
        'trend': 'ct',
        'level': 'c'
    }

    if type == 'adfuller':
        stats = adfuller(data, autolag = 'AIC')

        value = stats[0]
        pvalue = stats[1]
        pct_5 = stats[4]['5%']
        
    elif type.split('_')[0] == 'kpss':
        stats = kpss(data, regression = kpss_types[type.split('_')[1]])

        value = stats[0]
        pvalue = stats[1]
        pct_5 = stats[3]['5%']

    return (
        f'{value:.4f}',
        f'{pvalue:.4f}', 
        f'{pct_5:.4f}'
    )


def buy_and_hold(prices):
    returns = prices.pct_change()

    signals =  pd.DataFrame(
        index = prices.index
    )

    signals['price'] = prices
    signals['position'] = 1
    signals['returns'] = returns

    signals['strategy_returns'] = signals['position'].shift(1) * signals['returns']
    signals['cumulative'] = prices / prices.iloc[0]

    strat_returns = signals['strategy_returns'].dropna()
    total_return = (1 + strat_returns).prod() - 1

    sharpe = strat_returns.mean() / strat_returns.std() * np.sqrt(252)

    cumulative = (1 + strat_returns.fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'num_trades': 1
    }


def mean_reversion(prices, long, entry_threshold, exit_threshold):
    returns = prices.pct_change()

    ma_long = prices.rolling(long).mean()
    std_long = prices.rolling(long).std()
    z_score = (prices - ma_long) / std_long

    signals =  pd.DataFrame(
        index = prices.index
    )

    signals['price'] = prices
    signals['ma_long'] = ma_long
    signals['z_score'] = z_score
    signals['position'] = 0

    position = 0
    positions = []

    for i in range(len(signals)):
        if i < long:
            positions.append(0)
            continue
        
        current_z = signals['z_score'].iloc[i]
        
        if position == 0:
            if current_z < -entry_threshold:
                position = 1
            elif current_z > entry_threshold:
                position = -1
        elif position == 1 and current_z > -exit_threshold:
            position = 0
        elif position == -1 and current_z > exit_threshold:
            position = 0
        
        positions.append(position)
    
    signals['position'] = positions
    signals['returns'] = returns
    signals['strategy_returns'] = signals['position'].shift(1) * signals['returns']

    # Metrics

    total_return = (1 + signals['strategy_returns'].dropna()).prod() - 1
    sharpe = signals['strategy_returns'].mean() / signals['strategy_returns'].std() * np.sqrt(252)
    cumulative = (1 + signals['strategy_returns'].fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    trades = (signals['position'].diff() != 0).sum()

    return signals, {
        'total_return': total_return,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'num_trades': trades
    }


def plot_prices(signals, short, long, company_name):
    long_entries = signals[signals['position'].diff() == 1].index
    short_entries = signals[signals['position'].diff() == -1].index
    ma_short = signals['price'].rolling(short).mean()
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x = signals.index,
            y = signals['price'],
            mode = 'lines',
            name = f'{company_name} price',
            line = {
                'color': '#3366FF',
                'width': 2
            }
        )
    )

    fig.add_trace(
        go.Scatter(
            x = signals.index,
            y = signals['ma_long'],
            mode = 'lines',
            name = f'{long} days MA (long)',
            line = {
                'color': '#C2C61C',
                'width': 2
            }
        )
    )

    fig.add_trace(
        go.Scatter(
            x = signals.index,
            y = ma_short,
            mode = 'lines',
            name = f'{short} days MA (short)',
            line = {
                'color': '#DA7A32',
                'width': 2
            }
        )
    )

    fig.add_trace(
        go.Scatter(
            x = long_entries,
            y = signals.loc[long_entries, 'price'],
            name = 'Long Entry',
            mode = 'markers',
            marker = {
                'color': '#40C07C',
                'symbol': 'triangle-up',
                'size': 13
            }
        )
    )

    fig.add_trace(
        go.Scatter(
            x = short_entries,
            y = signals.loc[short_entries, 'price'],
            name = 'Short Entry',
            mode = 'markers',
            marker = {
                'color': '#DA3248',
                'symbol': 'triangle-down',
                'size': 13
            }
        )
    )

    fig.update_layout(
        title = {
            'text': 'Цены',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Цены ($)',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )    

    return fig


def plot_z_score(signals, entry_threshold, exit_threshold):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x = signals.index,
            y = signals['z_score'],
            mode = 'lines',
            name = 'z-score dynamic',
            line = {
                'color': '#3366FF',
                'width': 3
            }
        )
    )

    fig.add_hrect(
        y0 = entry_threshold,
        y1 = signals['z_score'].max(),
        fillcolor = '#DA3248',
        label = {
            'text': 'Entry Threshold',
            'textposition': 'bottom left'
            },
        opacity = 0.25,
        line = {
            'width': 1.0,
            'dash': 'dash',
            'color': '#1D1D1D'
        }
    )

    fig.add_hrect(
        y0 = exit_threshold,
        y1 = -exit_threshold,
        fillcolor = '#DA7A32',
        label = {
            'text': 'Exit Threshold',
            'textposition': 'top left'
            },
        opacity = 0.25,
        line = {
            'width': 1.0,
            'dash': 'dash',
            'color': '#1D1D1D'
        }
    )

    fig.add_hline(
        y = 0,
        line = {
            'width': 1.0,
            'color': "#1D1D1D"
        }
    )

    fig.add_hrect(
        y0 = -entry_threshold,
        y1 = signals['z_score'].min(),
        fillcolor = '#40C07C',
        opacity = 0.25,
        line = {
            'width': 1.0,
            'dash': 'dash',
            'color': '#1D1D1D'
        }
    )

    fig.update_layout(
        title = {
            'text': 'Z-score график',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Z-score',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    return fig


def plot_strategies(signals, strategies):
    fig = go.Figure()

    for i, (name, strategy) in enumerate(strategies.items()):
        fig.add_trace(
            go.Scatter(
                x = signals.index,
                y = strategy,
                mode = 'lines',
                name = name,
                line = {
                    'color': COLORS_BASE_THEME['categories'][f'category-{i + 1}'],
                    'width': 2                    
                }
            )
        )

    fig.update_layout(
        title = {
            'text': 'Сравнение стратегий',
            'font': {
                'size': 24,
                'color': COLORS_BASE_THEME['chart_title'],
                'weight': 500
            }
        },
        xaxis_title = 'Дата',
        yaxis_title = 'Доходности (%)',
        height = 400,
        margin = {
            'l': 20,
            'r': 20,
            't': 40,
            'b': 20
        },
        template = 'plotly_white'
    )

    fig.update_xaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    fig.update_yaxes(
        title_font=dict(size=18, color=COLORS_BASE_THEME['base_font']),
        tickfont=dict(size=14),
    )

    return fig