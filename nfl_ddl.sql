CREATE TABLE teams(
	team_id int PRIMARY KEY,
	conf text,
	division text,
	current_name text
);

CREATE TABLE teams_map(
	team_id int REFERENCES teams(team_id),
	year int,
	name text,
	PRIMARY KEY(team_id, year)
);

CREATE TABLE season_team_stats(
	team_id int REFERENCES teams(team_id),
	year int,
	wins int,
	losses int,
	ties int,
	points_for int,
	points_against int,
	strength_of_schedule float,
	PRIMARY KEY(team_id, year)
);

CREATE TABLE players(
	player_season_id int PRIMARY KEY,
	player_name text,
	year int,
	team_id int REFERENCES teams(team_id),
	position text
);

CREATE TABLE passing(
	player_season_id int REFERENCES players(player_season_id) PRIMARY KEY,
	games_started int,
	wins int,
	losses int,
	ties int, 
	completions int,
	attempts int,
	yards int,
	touchdowns int,
	interceptions int
);

CREATE TABLE rushing(
	player_season_id int REFERENCES players(player_season_id) PRIMARY KEY,
	games int,
	games_started int,
	attempts int,
	yards int,
	touchdowns int,
	fumbles int
);

CREATE TABLE receiving(
	player_season_id int REFERENCES players(player_season_id) PRIMARY KEY,
	games int,
	games_started int,
	targets int,
	receptions int,
	yards int,
	touchdowns int,
	fumbles int
);

CREATE TABLE defense(
	player_season_id int REFERENCES players(player_season_id) PRIMARY KEY,
	games int,
	games_started int,
	interceptions int,
	interception_yards int,
	interception_touchdowns int,
	fumbles_forced int,
	fumbles_recovered int,
	fumble_yards int,
	sacks float,
	solo_tackles float,
	assisted_tackles float,
	tackles_for_loss float
);

CREATE TABLE coaches(
	name text,
	year int,
	team_id int REFERENCES teams(team_id),
	wins int,
	losses int,
	ties int,
	PRIMARY KEY(name, year)
);

CREATE TABLE games(
	year int,
	week text,
	winner int REFERENCES teams(team_id),
	loser int REFERENCES teams(team_id),
	home_team int REFERENCES teams(team_id),
	points_winner int,
	points_loser int,
	yards_winner int,
	yards_loser int,
	turnovers_winner int,
	turnovers_loser int,
	PRIMARY KEY(year, week, winner)
);

CREATE TABLE awards(
	year int PRIMARY KEY,
	DPOY_position text,
	DPOY_player int REFERENCES players(player_season_id),
	OPOY_position text,
	OPOY_player int REFERENCES players(player_season_id),
	MVP_position text,
	MVP_player int REFERENCES players(player_season_id)
);

CREATE TABLE stadiums(
	name text PRIMARY KEY,
	year_from int,
	year_to int,
	city text,
	state text,
	team_list text
);
