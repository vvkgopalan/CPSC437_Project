import streamlit as st
import pandas as pd
from vega_datasets import data

import sqlalchemy
from sqlalchemy import create_engine
url = 'postgresql://admin:jntpjijh@35.230.82.92:13601/nfl'
engine = create_engine('postgresql://admin:jntpjijh@35.230.82.92:13601/nfl', echo=False)

@st.cache(hash_funcs={sqlalchemy.engine.Engine: lambda _: None})
def get_data(query):
    return pd.read_sql(query, engine)


# Modified from https://discuss.streamlit.io/t/table-of-contents-widget/3470/7
class Toc:

    def __init__(self):
        self._items = []
        self._placeholder = None
    
    def title(self, text):
        self._markdown(text, "h1")

    def header(self, text):
        self._markdown(text, "h2", " " * 2)

    def subheader(self, text):
        self._markdown(text, "h3", " " * 4)

    def placeholder(self, sidebar=False):
        self._placeholder = st.sidebar.empty() if sidebar else st.empty()

    def generate(self):
        if self._placeholder:
            self._placeholder.markdown("\n".join(self._items), unsafe_allow_html=True)
    
    def _markdown(self, text, level, space=""):
        key = "".join(filter(str.isalnum, text)).lower()

        st.markdown(f"<{level} id='{key}'>{text}</{level}>", unsafe_allow_html=True)
        self._items.append(f"{space}* <a href='#{key}'>{text}</a>")


toc = Toc()
toc.placeholder(True)
toc.title("Visualizations for NFL Database")



toc.header("Introduction")
"""
Welcome to our webpage!
"""


toc.header("Queries")


# Query 1
toc.subheader("Query 1")

with st.echo(code_location='below'):
    df = get_data('select * from teams;')
    st.write('Here is the table for the first query')
    st.write(df)


# Query 1
toc.subheader("Query 2")

with st.echo(code_location='below'):
    df = get_data('select * from season_team_stats;')
    st.write('Here is the table for the second query')
    st.write(df)


# Query 3
toc.subheader("Query 3")

with st.echo(code_location='below'):
    df = get_data('select * from players;')
    st.write('Here is the table for the last query')
    st.write(df)


# Generate table of contents
toc.generate()
