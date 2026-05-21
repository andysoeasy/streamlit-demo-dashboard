import streamlit as st
import pandas as pd

from config import (
    MONTH,
    YEARS,
    WEEKS,
    QUARTERS,
    COMPANIES
)

from backend.utils import (
    print_main_chart,
    print_returns_chart,
    print_volatility_chart,
    get_statistic_coefs,
    print_stat_card
)
from backend.data import (
    get_data,
    get_returns,
    get_volatility
)

st.set_page_config(
    page_title='Анализ стационарности',
    layout = 'wide'
)

st.header('Анализ стационарности')

if 'year' not in st.session_state:
    st.session_state.year = 'Не выбрано'
if 'quarter' not in st.session_state:
    st.session_state.quarter = 'Не выбрано'
if 'month' not in st.session_state:
    st.session_state.month = 'Не выбрано'
if 'week' not in st.session_state:
    st.session_state.week = 'Не выбрано'

year_val = st.session_state.year
quarter_val = st.session_state.quarter
month_val = st.session_state.month
week_val = st.session_state.week

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

    window = st.slider(
        'Окно',
        min_value=1,
        max_value=30,
        step=1,
        value=7
    )   

    companies = st.sidebar.multiselect(
        'Акции',
        COMPANIES,
        default = COMPANIES[0]
    )

    st.subheader('Справка')
    st.write(
        'Здесь использованы данные площадки Yahoo!Finance. Период сбора информации - последние 2 года, включая начало мая 2026 года.'
    )


main_data = get_data(
    companies, 
    YEARS[year_dropdown], 
    QUARTERS[quarter_dropdown], 
    MONTH[month_dropdown], 
    WEEKS[week_dropdown]
)

returns_data = get_returns(
    precompute_data = main_data
)

volatility_data = get_volatility(
    precompute_data = returns_data, 
    window = window
)

main_graph_col, stats_col = st.columns((7, 5))

with main_graph_col:
    st.plotly_chart(
        print_main_chart(main_data)
    )

with stats_col:
    adf_company, trend_company, level_company = st.columns(3)
    adf_val, trend_val, level_val = st.columns(3)
    adf_pval, trend_pval, level_pval = st.columns(3)
    adf_5pct, trend_5pct, level_5pct = st.columns(3)

    with adf_company:
        adf_dropdown = st.selectbox(
            'Компания для ADF',
            companies
        )
        
    with trend_company:
        trend_dropdown = st.selectbox(
            'Компания для KPSS(trend)',
            companies
        )

    with level_company:
        level_dropdown = st.selectbox(
            'Компания для KPSS(level)',
            companies
        )

    adf_tests = get_statistic_coefs(
        data = get_data(
            [adf_dropdown], 
            YEARS[year_dropdown],
            QUARTERS[quarter_dropdown], 
            MONTH[month_dropdown], 
            WEEKS[week_dropdown]
        ),
        type = 'adfuller'
    )

    trend_tests = get_statistic_coefs(
        data = get_data(
            [trend_dropdown], 
            YEARS[year_dropdown],
            QUARTERS[quarter_dropdown], 
            MONTH[month_dropdown], 
            WEEKS[week_dropdown]
        ),
        type = 'kpss_trend'
    )

    level_tests = get_statistic_coefs(
        data = get_data(
            [level_dropdown], 
            YEARS[year_dropdown],
            QUARTERS[quarter_dropdown], 
            MONTH[month_dropdown], 
            WEEKS[week_dropdown]
        ),
        type = 'kpss_level'
    )

    # adf test
    with adf_val:
        st.metric('ADF value', adf_tests[0])

    with adf_pval:
        st.metric('ADF p-value', adf_tests[1])

    with adf_5pct:
        st.metric('ADF 5 %', adf_tests[2])

    # KPSS trend test
    with trend_val:
        st.metric('KPSS(trend) value', trend_tests[0])

    with trend_pval:
        st.metric('KPSS(trend) p-value', trend_tests[1])

    with trend_5pct:
        st.metric('KPSS(trend) 5 %', trend_tests[2])

    # KPSS level test
    with level_val:
        st.metric('KPSS(level) value', level_tests[0])

    with level_pval:
        st.metric('KPSS(level) p-value', level_tests[1])

    with level_5pct:
        st.metric('KPSS(level) 5 %', level_tests[2])


returns_chart_col, vol_chart_col = st.columns((1, 1))

with returns_chart_col:
    st.plotly_chart(
        print_returns_chart(returns_data)
    )

with vol_chart_col:
    st.plotly_chart(
        print_volatility_chart(volatility_data)
    )
