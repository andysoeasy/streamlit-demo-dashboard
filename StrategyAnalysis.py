import streamlit as st
from config import (
    MONTH,
    YEARS,
    WEEKS,
    QUARTERS,
    COMPANIES,
    STRATEGIES
)

from backend.utils import (
    buy_and_hold,
    mean_reversion,
    plot_prices,
    plot_z_score,
    plot_strategies
)

from backend.data import get_data

st.set_page_config(
    page_title='Анализ стратегий',
    layout = 'wide'
)

st.header('Анализ стратегий')

if 'year' not in st.session_state:
    st.session_state.year = 'Не выбрано'
if 'quarter' not in st.session_state:
    st.session_state.quarter = 'Не выбрано'
if 'month' not in st.session_state:
    st.session_state.month = 'Не выбрано'
if 'week' not in st.session_state:
    st.session_state.week = 'Не выбрано'

if not (st.session_state.year != 'Не выбрано'):
    disable_quarter = True
    disable_month = True
    disable_week = True
else:
    if st.session_state.quarter != 'Не выбрано':
        disable_quarter = False
        disable_month = True
        disable_week = True

        if st.session_state.month != 'Не выбрано':
            st.session_state.month = 'Не выбрано'
        if st.session_state.week != 'Не выбрано':
            st.session_state.week = 'Не выбрано'

    elif st.session_state.month != 'Не выбрано':
        disable_quarter = True
        disable_month = False
        disable_week = False
    
    else:
        disable_quarter = False
        disable_month = False
        disable_week = True


with st.sidebar:
    st.header('Фильтры')

    st.subheader('Период')

    year_col, quarter_col = st.columns(2)
    month_col, week_col = st.columns(2)

    with year_col:
        year_dropdown = st.selectbox(
            'Год',
            YEARS.keys(),
            key = 'year',
        )
    
    with quarter_col:
        quarter_dropdown = st.selectbox(
            'Квартал',
            QUARTERS.keys(),
            key = 'quarter',
            disabled = disable_quarter
        )

    with month_col:
        month_dropdown = st.selectbox(
            'Месяц',
            MONTH.keys(),
            key = 'month',
            disabled = disable_month
        ) 

    with week_col:
        week_dropdown = st.selectbox(
            'Неделя',
            WEEKS.keys(),
            key = 'week',
            disabled = disable_week
        )

    long_window = st.slider(
        'Long Window',
        min_value=28,
        max_value=252,
        step=1,
        value=28
    )

    short_window = st.slider(
        'Short Window',
        min_value=1,
        max_value=27,
        step=1,
        value=7
    )

    entry_threshold = st.number_input(
        'Entry Threshold',
        min_value = 0.01,
        max_value = 5.0,
        value = 1.57,
        step = 0.01
    )

    exit_threshold = st.number_input(
        'Exit Threshold',
        min_value = 0.01,
        max_value = 5.0,
        value = 0.25,
        step = 0.01
    )  

    company = st.selectbox(
        'Акции',
        COMPANIES
    )

    strategy = st.selectbox(
        'Стратегия',
        options = STRATEGIES

    )

    st.subheader('Справка')
    st.write(
        'Здесь использованы данные площадки Yahoo!Finance. Период сбора информации - последние 2 года, включая начало мая 2026 года.'
    )


data = get_data(
    [company],
    YEARS[year_dropdown], 
    QUARTERS[quarter_dropdown], 
    MONTH[month_dropdown], 
    WEEKS[week_dropdown]
)

strat_names = {
    'Mean Reversion': mean_reversion
}

prices = data.squeeze()
signals, metrics_strategy = strat_names['Mean Reversion'](
    prices,
    long = long_window,
    entry_threshold = entry_threshold,
    exit_threshold = exit_threshold
)

benchmark_strategy = prices / prices.iloc[0]
metrics_benchmark = buy_and_hold(prices)

mean_reversion_strat = (1 + signals['strategy_returns'].fillna(0)).cumprod()

strategies = {
    'Buy&Hold': benchmark_strategy,
    'Mean-Reversion': mean_reversion_strat
}

main_chart_col, metrics_col = st.columns((8, 4))
z_score_chart_col, prices_chart_col = st.columns((5, 7))

with main_chart_col:
    st.plotly_chart(
        plot_strategies(
            signals,
            strategies
        )
    )

with metrics_col:
    benchmark_col, strategy_col = st.columns(2)

    with benchmark_col:
        st.subheader('Метрики бенчмарка')

        st.metric(
            'Общая доходность',
            f'{metrics_benchmark['total_return'] * 100:.3f} %'
        )

        st.metric(
            'Sharpe Ratio',
            f'{metrics_benchmark['sharpe_ratio']:.3f}'
        )

        st.metric(
            'Просадки',
            f'{metrics_benchmark['max_drawdown'] * 100:.3f} %'
        )

        st.metric(
            'Количество сделок',
            metrics_benchmark['num_trades']
        )
    
    with strategy_col:
        st.subheader('Метрики стратегии')

        st.metric(
            'Общая доходность',
            f'{metrics_strategy['total_return'] * 100:.3f} %'
        )

        st.metric(
            'Sharpe Ratio',
            f'{metrics_strategy['sharpe_ratio']:.3f}'
        )

        st.metric(
            'Просадки',
            f'{metrics_strategy['max_drawdown'] * 100:.3f} %'
        )

        st.metric(
            'Количество сделок',
            metrics_strategy['num_trades']
        )


with z_score_chart_col:
    st.plotly_chart(
        plot_z_score(
            signals,
            entry_threshold,
            exit_threshold
        )
    )

with prices_chart_col:
    st.plotly_chart(
        plot_prices(
            signals,
            short_window,
            long_window,
            company
        )
    )
