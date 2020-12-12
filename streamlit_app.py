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


## Static visualization of teams since 2002 ordered by wins
toc.header("Teams Ordered By Wins (Since 2002)")
query = """
SELECT name AS "Team Name", year, wins, losses, ties, points_for, points_against FROM season_team_stats, teams_map WHERE season_team_stats.team_id = teams_map.team_id AND teams_map.year_from <= season_team_stats.year AND season_team_stats.year <= teams_map.year_to;
"""
df = get_data(query)
df = df.fillna(0)
df.columns = df.columns.str.replace("_", " ").str.title()
df.sort_values(["Wins", "Year"], ascending=False, inplace=True)
st.write(df)



## Todo: 2020 team predictions based on similarity. Maybe this also has us predict the superbowl winner and player award winners.


## Stats of MVP Winners
toc.header("Most Valuable Player (MVP) Winner Statistics")
query = """
SELECT awards.year, player_name, mvp_position AS position, teams_map.name AS team, season_team_stats.wins, season_team_stats.losses, season_team_stats.ties,
    passing.yards AS "passing_yards", passing.touchdowns AS "passing_TD", rushing.yards AS "rushing_yards", rushing.touchdowns AS "rushing_TD", receiving.yards AS "receiving_yards", receiving.touchdowns AS "receiving_TD"
FROM awards
LEFT JOIN players ON mvp_player = players.player_season_id
LEFT JOIN teams_map ON teams_map.team_id = players.team_id AND teams_map.year_from <= awards.year AND awards.year <= teams_map.year_to
LEFT JOIN season_team_stats ON season_team_stats.team_id = teams_map.team_id AND season_team_stats.year = awards.year
LEFT JOIN passing ON mvp_player = passing.player_season_id
LEFT JOIN rushing ON mvp_player = rushing.player_season_id
LEFT JOIN receiving ON mvp_player = receiving.player_season_id;
"""
df = get_data(query)
df = df.fillna(0)
df.columns = df.columns.str.replace("_", " ").str.title().str.replace("Td", "TD")
df.insert(7, "Total Yards", df["Passing Yards"]+df["Rushing Yards"]+df["Receiving Yards"])
df.insert(7, "Total TD", df["Passing TD"]+df["Rushing TD"]+df["Receiving TD"])
df.sort_values(["Total TD", "Total Yards"], ascending=False, inplace=True)
st.write(df)


## Stats of OPOY Winners
toc.header("Offensive Player of the Year (OPOY) Winner Statistics")
query = """
SELECT awards.year, player_name, opoy_position AS position, teams_map.name AS team, season_team_stats.wins, season_team_stats.losses, season_team_stats.ties,
    passing.yards AS "passing_yards", passing.touchdowns AS "passing_TD", rushing.yards AS "rushing_yards", rushing.touchdowns AS "rushing_TD", receiving.yards AS "receiving_yards", receiving.touchdowns AS "receiving_TD"
FROM awards
LEFT JOIN players ON opoy_player = players.player_season_id
LEFT JOIN teams_map ON teams_map.team_id = players.team_id AND teams_map.year_from <= awards.year AND awards.year <= teams_map.year_to
LEFT JOIN season_team_stats ON season_team_stats.team_id = teams_map.team_id AND season_team_stats.year = awards.year
LEFT JOIN passing ON opoy_player = passing.player_season_id
LEFT JOIN rushing ON opoy_player = rushing.player_season_id
LEFT JOIN receiving ON opoy_player = receiving.player_season_id;
"""
df = get_data(query)
df = df.fillna(0)
df.columns = df.columns.str.replace("_", " ").str.title().str.replace("Td", "TD")
df.insert(7, "Total Yards", df["Passing Yards"]+df["Rushing Yards"]+df["Receiving Yards"])
df.insert(7, "Total TD", df["Passing TD"]+df["Rushing TD"]+df["Receiving TD"])
df.sort_values(["Total TD", "Total Yards"], ascending=False, inplace=True)
st.write(df)


## Stats of DPOY Winners
toc.header("Defensive Player of the Year (DPOY) Winner Statistics")
query = """
SELECT awards.year, player_name, dpoy_position AS position, teams_map.name AS team, season_team_stats.wins, season_team_stats.losses, season_team_stats.ties,
    solo_tackles, assisted_tackles, fumbles_forced, interceptions, sacks
FROM awards
LEFT JOIN players ON dpoy_player = players.player_season_id
LEFT JOIN teams_map ON teams_map.team_id = players.team_id AND teams_map.year_from <= awards.year AND awards.year <= teams_map.year_to
LEFT JOIN season_team_stats ON season_team_stats.team_id = teams_map.team_id AND season_team_stats.year = awards.year
LEFT JOIN defense ON dpoy_player = defense.player_season_id;
"""
df = get_data(query)
df = df.fillna(0)
df.columns = df.columns.str.replace("_", " ").str.title()
df.insert(7, "Total Tackles", df["Solo Tackles"]+df["Assisted Tackles"])
df.sort_values(["Total Tackles", "Year"], ascending=False, inplace=True)
st.write(df)

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

# Visualization of winningest coaches, losingest coaches.
toc.header("Winning-est/Losing-est Coaches")
coach_option = st.radio("Select Aggregation Option (min 16 games)", ('Losing-est (Coach & Team)', 'Losing-est (Overall)', 'Winning-est (Coach & Team)', 'Winning-est (Overall)'))

if coach_option == 'Losing-est (Coach & Team)':
    query = '''SELECT name as "Name", SUM(wins) as "Wins", SUM(losses) AS "Losses", current_name AS "Team"
    FROM coaches JOIN teams ON teams.team_id = coaches.team_id GROUP BY name, "Team" HAVING SUM(losses) + SUM(wins) >= 16 ORDER BY cast(SUM(wins) AS float)/SUM(losses) ASC'''
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
elif coach_option == 'Losing-est (Overall)':
    query = '''SELECT name as "Name", SUM(wins) as "Wins", SUM(losses) AS "Losses"
    FROM coaches GROUP BY name HAVING SUM(losses) + SUM(wins) >= 16 ORDER BY cast(SUM(wins) AS float)/SUM(losses) ASC'''
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
elif coach_option == 'Winning-est (Coach & Team)':
    query = '''SELECT name as "Name", SUM(wins) as "Wins", SUM(losses) AS "Losses", current_name AS "Team"
    FROM coaches JOIN teams ON teams.team_id = coaches.team_id GROUP BY name, "Team" HAVING SUM(losses) + SUM(wins) >= 16 ORDER BY cast(SUM(wins) AS float)/SUM(losses) DESC'''
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)
elif coach_option == 'Winning-est (Overall)':
    query = '''SELECT name as "Name", SUM(wins) as "Wins", SUM(losses) AS "Losses"
    FROM coaches GROUP BY name HAVING SUM(losses) + SUM(wins) >= 16 ORDER BY cast(SUM(wins) AS float)/SUM(losses) DESC'''
    df = get_data(query)
    df = df.fillna(0)
    st.write(df)

## toughest stadiums visualization (maybe bar chart on top of table)
toc.header("Toughest Stadiums to Play In")

@st.cache(hash_funcs={sqlalchemy.engine.Engine: lambda _: None})
def get_stadium_strengths():
    games_data = pd.read_sql("SELECT winner, loser, home_team, year FROM games;", engine)
    stadiums_data = pd.read_sql("SELECT name, year_from, year_to, team_list FROM stadiums;", engine)
    team_id_to_team = pd.read_sql("SELECT team_id, current_name FROM teams;", engine)
    teams_dict = team_id_to_team.set_index('team_id').to_dict()['current_name']

    games_data["home_win"] = games_data["winner"] == games_data["home_team"]
    games_data["home_loss"] = games_data["loser"] == games_data["home_team"]
    games_data["winner"] = games_data["winner"].apply(lambda s: teams_dict[s])
    games_data["loser"] = games_data["loser"].apply(lambda s: teams_dict[s])
    games_data["home_team"] = games_data["home_team"].apply(lambda s: teams_dict[s])

    stadium_list = []
    for i, row in games_data.iterrows():
        found = False
        if pd.isna(row["home_team"]):
            stadium_list.append("Neutral Site")
            continue

        for j, stadium in stadiums_data.iterrows():
            if pd.isna(stadium['team_list']):
                continue

            if row['year'] >= stadium['year_from'] and row['year'] <= stadium['year_to'] and row["home_team"] in stadium['team_list']:
                stadium_list.append(str(stadium['name']))
                found = True
                break

        if not found:
            stadium_list.append("Neutral Site")

    games_data["stadiums"] = stadium_list
    games_data = games_data[games_data['stadiums'] != "Neutral Site"]
    summarize_stadiums = games_data.groupby(['stadiums'])[['home_win', 'home_loss']].sum()
    summarize_stadiums["W/L"] = summarize_stadiums['home_win']/summarize_stadiums['home_loss']
    return summarize_stadiums

stadium_strengths = get_stadium_strengths()
st.write(stadium_strengths.sort_values(by='W/L', ascending=False))

## 10 best home recods
barfig = plt.figure()
barax = barfig.add_axes([0,0,1,1])
stadiums = stadium_strengths.sort_values(by='W/L', ascending=False).index.tolist()[0:10]
wls = stadium_strengths.sort_values(by='W/L', ascending=False)['W/L'][0:10]
barax.bar(stadiums,wls)
plt.xticks(rotation = 'vertical')
st.write(barfig)

## 10 worst home records
barfig = plt.figure()
barax = barfig.add_axes([0,0,1,1])
stadiums = stadium_strengths.sort_values(by='W/L', ascending=True).index.tolist()[0:10]
wls = stadium_strengths.sort_values(by='W/L', ascending=True)['W/L'][0:10]
barax.bar(stadiums,wls)
plt.xticks(rotation = 'vertical')
st.write(barfig)

# Generate table of contents
toc.generate()
