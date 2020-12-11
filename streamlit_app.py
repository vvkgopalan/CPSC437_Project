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


page_title = "Visualizations for NFL Database"
st.set_page_config(page_title=page_title, page_icon=
    "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/National_Football_League_logo.svg/1920px-National_Football_League_logo.svg.png")


toc = Toc()
toc.placeholder(True)
toc.title(page_title)


toc.header("Introduction")
"""
Welcome to our webpage!
"""


toc.header("Queries")


# Query 1
toc.subheader("Yearly Player Statistics")
aggr_stat = st.multiselect("View 2002-2020 Player Statistics", ['Passing', 'Rushing', 'Receiving', 'Defense'], [])
query_years = st.multiselect("Select Years (default all)", [str(year) for year in range(2002, 2021)], [str(year) for year in range(2002, 2021)])

teams = list(get_data("SELECT current_name from teams;")['current_name'])
query_teams = st.multiselect("Select Teams (default all)", teams, teams)

year_query = ""
if len(query_years) > 1:
    year_query = "AND players.year IN {}".format(tuple(query_years))
elif len(query_years) == 1:
    year_query = "AND players.year = {}".format(query_years[0])

team_query = ""
if len(query_teams) > 1:
    team_query = "AND teams.current_name IN {}".format(tuple(query_teams))
elif len(query_teams) == 1:
    team_query = "AND teams.current_name = '{}'".format(query_teams[0])


if 'Passing' in aggr_stat:
    st.subheader("Passing Data")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", wins AS "Wins", losses AS "Losses", 
    ties AS "Ties", completions AS "Comp", attempts AS "Att", cast(completions AS float)/attempts AS "Percent Completed",
    yards AS "Yds", cast(yards AS float)/attempts AS "Yards per Attempt", touchdowns AS "TD", interceptions AS "Int"
    FROM (SELECT * FROM passing JOIN players ON players.player_season_id = passing.player_season_id AND players.position LIKE '%QB%' {year_qry}) 
    AS passers JOIN teams ON passers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Rushing' in aggr_stat:
    st.subheader("Rushing Data")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    attempts AS "Att", yards AS "Yds", cast(yards AS float)/attempts AS "Yards per Attempt", touchdowns AS "TD", fumbles AS "Fmb"
    FROM (SELECT * FROM rushing JOIN players ON players.player_season_id = rushing.player_season_id AND rushing.yards > 50 {year_qry}) 
    AS rushers JOIN teams ON rushers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Receiving' in aggr_stat:
    st.subheader("Receiving Data")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    receptions AS "Rec", targets AS "Tgt", cast(receptions AS float)/targets AS "Percent Caught", touchdowns AS "TD", fumbles AS "Fmb"
    FROM (SELECT * FROM receiving JOIN players ON players.player_season_id = receiving.player_season_id AND receiving.yards > 50 {year_qry}) 
    AS receivers JOIN teams ON receivers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Defense' in aggr_stat:
    st.subheader("Defense Data")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    interceptions AS "Int", interception_yards AS "IntYds", interception_touchdowns AS "IntTD", fumbles_forced AS "FF", fumbles_recovered AS "FR",
    fumble_yards AS "FmbYards", fumble_touchdowns AS "FmbTD", sacks as "Sacks", assisted_tackles AS "Asst", solo_tackles AS "Solo", solo_tackles + assisted_tackles AS "Tot",
    tackles_for_loss AS "TFL" 
    FROM (SELECT * FROM defense JOIN players ON players.player_season_id = defense.player_season_id AND defense.games_started > 1 {year_qry}) 
    AS defenders JOIN teams ON defenders.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
    
# Generate table of contents
toc.generate()
