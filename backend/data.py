import pandas as pd
from config import DATA_DIR
import streamlit as st


def load_company_data(company):
    df = pd.read_csv(DATA_DIR / f'{company}_last2y.csv')

    df['Date']= pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.dropna(inplace = True)

    return df['Close']


def get_time_mask(df, year = None, quarter = None, month = None, week = None):
    if year is None and quarter is None and month is None and week is None:
        return df

    dt = df.index

    mask = pd.Series(True, index = df.index)

    if year:
        mask &= dt.year == year
    
    if quarter:
        mask &= dt.quarter == quarter

    if month:
        mask &= dt.month == month

    if week:
        week_of_month = ((dt.day - 1) // 7) + 1
        mask &= week_of_month == week

    return df.loc[mask]


def get_resample_rule(year = None, quarter = None, month = None, week = None):
    if week:
        return 'D'
    elif month:
        return 'D'
    elif quarter:
        return 'W'
    elif year:
        return 'ME'
    else:
        return None
    

def validate_filters(year, quarter, month, week):
    if quarter and not year:
        return 'Чтобы выбрать квартал, сначала выберите год'
    
    if month and not year:
        return 'Чтобы выбрать месяц, сначала выберите год'
    
    if week and not (year and month):
        return 'Чтобы выбрать неделю, сначала выберите год и месяц'
    
    if month and quarter:
        return 'Нельзя одновременно выбрать квартал и месяц'
    
    
@st.cache_data
def get_data(companies, year = None, quarter = None, month = None, week = None):
    validate_filters(year, quarter, month, week)

    data_dict = {}

    for company in companies:
        raw_data = load_company_data(company)
        filtered_data = get_time_mask(raw_data, year, quarter, month, week)

        freq_rule = get_resample_rule(year, quarter, month, week)
        if freq_rule:
            resampled_data = filtered_data.resample(freq_rule).mean()
        else:
            resampled_data = filtered_data
        
        clean_data = resampled_data.dropna(how = 'all')
        clean_data.name = company

        data_dict[company] = clean_data

    final_data = pd.concat(data_dict, axis = 1)
    final_data.sort_index(inplace = True)

    return final_data    


@st.cache_data
def get_returns(companies = None, year = None, quarter = None, month = None, week = None, precompute_data = None):

    if precompute_data is None:
        data = get_data(companies, year, quarter, month, week)
    else:
        data = precompute_data

    returns = data.pct_change()
    returns.dropna(inplace = True)

    return returns


@st.cache_data
def get_volatility(companies = None, year = None, quarter = None, month = None, week = None, window = 30, precompute_data = None):

    if precompute_data is None:
        returns = get_returns(companies, year, quarter, month, week)
    else:
        returns = precompute_data

    volatility = returns.rolling(window).std()
    volatility.dropna(inplace = True)

    return volatility
