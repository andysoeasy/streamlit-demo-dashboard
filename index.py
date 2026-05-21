import streamlit as st

pages = st.navigation([
    st.Page(
        page = 'StationaryAnalysis.py',
        title = 'Анализ стационарности'
    ),
    st.Page(
        page = 'StrategyAnalysis.py',
        title = 'Анализ стратегий'
    )
])

pages.run()