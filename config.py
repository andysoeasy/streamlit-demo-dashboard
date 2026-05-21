from pathlib import Path

YEARS = {
    'Не выбрано': None,
    2025: 2025,
    2026: 2026
}

QUARTERS = {
    'Не выбрано': None,
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4
}

MONTH = {
    'Не выбрано': None,
    'Январь': 1,
    'Февраль': 2,
    'Март': 3,
    'Апрель': 4,
    'Май': 5,
    'Июнь': 6,
    'Июль': 7, 
    'Август': 8, 
    'Сентябрь': 9, 
    'Октябрь': 10, 
    'Ноябрь': 11, 
    'Декабрь': 12
}

WEEKS = {
    'Не выбрано': None,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5
}

COMPANIES = [
    'EURGBP=X',
    'AAPL', 
    'MSFT', 
    'GOOGL', 
    'AMZN', 
    'META', 
    'TSLA', 
    'NVDA',
    'TSM',
    'BTC-USD',
    'ETH-USD'
]


STRATEGIES = ['MR']
CATEGORIES = {
    company: category 
    for company, category in zip(COMPANIES, [f'category-{i}' for i in range(1, len(COMPANIES) + 1)])
}
DATA_DIR = Path('data')

COLOR_MAP = {
    'AAPL': '#1f77b4',
    'MSFT': '#ff7f0e',
    'GOOGL': '#2ca02c',
    'AMZN': '#d62728',
    'META': '#9467bd',
    'TSLA': '#8c564b',
    'NVDA': '#e377c2',
    'NFLX': '#7f7f7f',
}

COLORS_BASE_THEME = {
    'base_font': '#262626',
    'background_chart': '#f8f9fa',
    'background_color': '#ADC2FF',
    'main_title': '#3366FF',
    'chart_title': '#DA3248',
    'base_color': '#CCCCCC',
    'categories': {
        'category-1': '#3366FF',
        'category-2': '#C2C61C',
        'category-3': '#DA7A32',
        'category-4': '#C04052',
        'category-5': "#40C07C",
        'category-6': "#A040C0",
        'category-7': "#388CD1",
        'category-8': "#e377c2",
        'category-9': "#8c564b",
        'category-10': "#9467bd",
        'category-11': "#7f7f7f",
        'category-12': "#1f77b4"
    }
}