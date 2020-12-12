import streamlit as st
import pandas as pd
from vega_datasets import data
from matplotlib import pyplot as plt
from matplotlib import cm as cm
import numpy as np
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

## Dynamic visualization of player statistics per year 
toc.header("Yearly Player Statistics")
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
    st.subheader("Player Passing Data (QB Only)")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", wins AS "Wins", losses AS "Losses", 
    ties AS "Ties", completions AS "Comp", attempts AS "Att", cast(completions AS float)/attempts AS "Percent Completed",
    yards AS "Yds", cast(yards AS float)/attempts AS "Yards per Attempt", touchdowns AS "TD", interceptions AS "Int"
    FROM (SELECT * FROM passing JOIN players ON players.player_season_id = passing.player_season_id AND players.position LIKE '%QB%' {year_qry}) 
    AS passers JOIN teams ON passers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Rushing' in aggr_stat:
    st.subheader("Player Rushing Data (> 50 Yards)")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    attempts AS "Att", yards AS "Yds", cast(yards AS float)/attempts AS "Yards per Attempt", touchdowns AS "TD", fumbles AS "Fmb"
    FROM (SELECT * FROM rushing JOIN players ON players.player_season_id = rushing.player_season_id AND rushing.yards > 50 {year_qry}) 
    AS rushers JOIN teams ON rushers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Receiving' in aggr_stat:
    st.subheader("Player Receiving Data (> 50 Yards)")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    receptions AS "Rec", targets AS "Tgt", cast(receptions AS float)/targets AS "Percent Caught", yards as "Yds", touchdowns AS "TD", fumbles AS "Fmb"
    FROM (SELECT * FROM receiving JOIN players ON players.player_season_id = receiving.player_season_id AND receiving.yards > 50 {year_qry}) 
    AS receivers JOIN teams ON receivers.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
if 'Defense' in aggr_stat:
    st.subheader("Player Defense Data (> 1 Game)")
    query = '''SELECT player_name AS "Name", year AS "Year", current_name AS "Team", games_started AS "Games Started", 
    interceptions AS "Int", interception_yards AS "IntYds", interception_touchdowns AS "IntTD", fumbles_forced AS "FF", fumbles_recovered AS "FR",
    fumble_yards AS "FmbYards", fumble_touchdowns AS "FmbTD", sacks as "Sacks", assisted_tackles AS "Asst", solo_tackles AS "Solo", solo_tackles + assisted_tackles AS "Tot",
    tackles_for_loss AS "TFL" 
    FROM (SELECT * FROM defense JOIN players ON players.player_season_id = defense.player_season_id AND defense.games_started > 1 {year_qry}) 
    AS defenders JOIN teams ON defenders.team_id = teams.team_id {team_qry};'''.format(year_qry=year_query, team_qry=team_query)
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)

## Dynamic visualization of team statistcs per year. 
## Todo: Add info from season_team_stats
toc.header("Yearly Team Statistics")
aggr_team_stat = st.multiselect("View 2002-2020 Team Statistics", ['Passing', 'Rushing', 'Receiving', 'Defense'], [])
query_team_years = st.multiselect("Select Years for Aggregation (default all)", [str(year) for year in range(2002, 2021)], [str(year) for year in range(2002, 2021)])

query_team_teams = st.multiselect("Select Teams for Aggregation (default all)", teams, teams)

team_year_query = ""
if len(query_team_years) > 1:
    team_year_query = "AND players.year IN {}".format(tuple(query_team_years))
elif len(query_team_years) == 1:
    team_year_query = "AND players.year = {}".format(query_team_years[0])

team_team_query = ""
if len(query_team_teams) > 1:
    team_team_query = "AND teams.current_name IN {}".format(tuple(query_team_teams))
elif len(query_team_teams) == 1:
    team_team_query = "AND teams.current_name = '{}'".format(query_team_teams[0])
    
if 'Passing' in aggr_team_stat:
    st.subheader("Team Passing Data")
    query = '''SELECT "Team", "Comp", "Att", "Yds", "TD", "Int", passing_teams.year, passing_teams.team_id, season_team_stats.team_id AS s_team_id FROM
    (SELECT teams.current_name AS "Team", completions AS "Comp", attempts AS "Att", yards AS "Yds", touchdowns AS "TD", interceptions AS "Int", passers.year, passers.team_id
    FROM (SELECT SUM(completions) AS completions, SUM(attempts) AS attempts, SUM(yards) as yards, SUM(touchdowns) AS touchdowns, SUM(interceptions) AS interceptions, players.team_id, players.year 
    FROM passing JOIN players ON players.player_season_id = passing.player_season_id {year_qry} GROUP BY players.team_id, players.year) 
    AS passers JOIN teams ON passers.team_id = teams.team_id {team_qry}) AS passing_teams JOIN season_team_stats ON season_team_stats.year = passing_teams.year;'''.format(year_qry=team_year_query, team_qry=team_team_query)
    df = get_data(query)
    df = df.fillna(0)
    df = df[df['s_team_id'] == df['team_id']] #some strange stuff is happening w/ the query if I add this as a second condition for the join...
    df = df.drop(['s_team_id', 'team_id'], axis = 1) 
    st.write(df)
if 'Rushing' in aggr_team_stat:
    st.subheader("Team Rushing Data")
    query = '''SELECT "Team", "Att", "Yds", "TD", "Fmb", rushing_teams.year, rushing_teams.team_id, season_team_stats.team_id AS s_team_id FROM
    (SELECT teams.current_name AS "Team", attempts AS "Att", yards AS "Yds", touchdowns AS "TD", fumbles AS "Fmb", rushers.year, rushers.team_id
    FROM (SELECT  SUM(attempts) AS attempts, SUM(yards) as yards, SUM(touchdowns) AS touchdowns, SUM(fumbles) AS fumbles, players.team_id, players.year 
    FROM rushing JOIN players ON players.player_season_id = rushing.player_season_id {year_qry} GROUP BY players.team_id, players.year) 
    AS rushers JOIN teams ON rushers.team_id = teams.team_id {team_qry}) AS rushing_teams JOIN season_team_stats ON season_team_stats.year = rushing_teams.year;'''.format(year_qry=team_year_query, team_qry=team_team_query)
    df = get_data(query)
    df = df.fillna(0)
    df = df[df['s_team_id'] == df['team_id']] #some strange stuff is happening w/ the query if I add this as a second condition for the join...
    df = df.drop(['s_team_id', 'team_id'], axis = 1)
    st.write(df)
if 'Receiving' in aggr_team_stat:
    st.subheader("Team Receiving Data")
    query = '''SELECT "Team", "Rec", "Tgt", "Yds", "TD", "Fmb", receiving_teams.year, receiving_teams.team_id, season_team_stats.team_id AS s_team_id FROM
    (SELECT teams.current_name AS "Team", receptions AS "Rec", targets AS "Tgt", yards AS "Yds", touchdowns AS "TD", fumbles AS "Fmb", receivers.year, receivers.team_id
    FROM (SELECT  SUM(receptions) AS receptions, SUM(targets) AS targets, SUM(yards) as yards, SUM(touchdowns) AS touchdowns, SUM(fumbles) AS fumbles, players.team_id, players.year 
    FROM receiving JOIN players ON players.player_season_id = receiving.player_season_id {year_qry} GROUP BY players.team_id, players.year) 
    AS receivers JOIN teams ON receivers.team_id = teams.team_id {team_qry}) AS receiving_teams JOIN season_team_stats ON season_team_stats.year = receiving_teams.year;'''.format(year_qry=team_year_query, team_qry=team_team_query)
    df = get_data(query)
    df = df.fillna(0)
    df = df[df['s_team_id'] == df['team_id']] #some strange stuff is happening w/ the query if I add this as a second condition for the join...
    df = df.drop(['s_team_id', 'team_id'], axis = 1)
    st.write(df)
if 'Defense' in aggr_team_stat:
    st.subheader("Teme Defense Data")
    # Todo
    st.write(df)

## Todo: static visualization of the best QBs, RBs, WRs since 2002 in aggregate, one ordered by Yds and another ordered by TD
## Todo: static visualization of teams since 2002 ordered by wins (essentially outputting season_team_stats - just want to display points for and points against)
## Todo: toughest stadiums visualization (maybe bar chart on top of table)
## Todo: 2020 team predictions based on similarity. Maybe this also has us predict the superbowl winner and player award winners.
## Todo: output stats of award winners
## Todo: static visualization of winningest coaches, losingest coaches.

## Vivek stretch todo: scorigami  
toc.header("NFL Scorigami")
scores = get_data("SELECT DISTINCT points_winner, points_loser FROM games;")
W_MAX = max(scores['points_winner'])
L_MAX = max(scores['points_loser'])
scores = scores.fillna(0)
data = [[0 for i in range(int(W_MAX)+1)] for j in range(int(L_MAX)+1)]
for i, row in scores.iterrows():
    data[int(row['points_loser'])][int(row['points_winner'])] += 1

fig = plt.figure()
ax = fig.add_subplot(111)
cmap = cm.get_cmap('Greens', 100)
ax.xaxis.tick_top()
ax.imshow(data, interpolation = "nearest", cmap=cmap)
ax.grid(True)
ax.set_xticks(np.arange(0, W_MAX, 1));
ax.set_yticks(np.arange(0, L_MAX, 1));
plt.xticks(fontsize=6, rotation = 'vertical')
plt.yticks(fontsize=6)
fig.tight_layout()
st.write(fig)

# Generate table of contents
toc.generate()
