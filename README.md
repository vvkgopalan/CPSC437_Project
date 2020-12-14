# NFL Database Final Project (CPSC 437)

Teammates: SK Bong (skb46) and Vivek Gopalan (vyg2)

In this repository, we have the data, DDL (for the database), and other code that was used to complete the project:

## Data

The data (scraped from `www.pro-football-reference.com`) is stored in each of the folders (for each year from 2002 to 2020). We restricted it to this range because teams have not changed since 2002 (minus some small location/name changes) which made it possible to compare the data for these years. The data in this repository is organized as follows:
* Year (e.g. 2020)
  * AFC.csv - season team statistics for teams in the American Football Conference
  * NFC.csv - season team statistics for teams in the National Football Conference
  * coaches.csv - coaches and their team/career/playoffs records
  * draft.csv - the order of players drafted
  * games.csv - information on the schedule of games played (with points and yards)
    * playoff_results.csv - same except for playoffs (information duplicated in games.csv)
  * defense.csv, kicking.csv, passing.csv, receiving.csv, returns.csv, rushing.csv - corresponding statistics per player
* DPOY.csv - Defensive Player of the Year award winners (year, name, team name, position)
* MVP.csv - Most Valuable Player award winners (year, name, team name, position)
* OPOY.csv - Offensive Player of the Year award winners (year, name, team name, position)
* stadiums.csv - Stadium name, years it was used, city, state, and teams that used the stadium

To view how we scraped the data, please see `scraper.ipynb`.

## Data Definition Language (DDL)

The DDL for our database schema can be found in `nfl_ddl.sql`.

## Underlying Database

We used YugabyteDB as our underlying database. YugabyteDB is an open-source distributed key-value store forked from RocksDB. It has three APIs for data access: YSQL (Postgres wire-compatible), YCQL (Cassandra wire-compatible) and YEDIS (REDIS wire-compatible). We created a YSQL database and deployed it on K8s in GCP using Yugabyte's Cloud Platform. The cluster is a 3-node cluster with a replication factor of 3. We additionally created a backup database in case we perform some unintentional writes / schema alterations or data is otherwise corrupted in our primary database. This serves to add redundancy. 

All queries written are PGSQL compatible. 

To access the database directly, please follow the instructions here: https://download.yugabyte.com/. After you have downloaded and extracted the yugabyte-db `tar.gz`, please use the following command to connect to the database: `PGPASSWORD=jntpjijh ./bin/ysqlsh -h 35.230.82.92 -p 13601 -U admin -d nfl`

## Data Cleaning and Insertion

To insert the data into our database, we used a jupyter notebook `Table_Cleaning.ipynb` to clean and modify the scraped data into the desired format. This notebook uses sqlalchemy to create a SQL engine that connects to our database which can be used with the `to_sql()` function to insert the data from pandas dataframes.

## Streamlit Webpage

The webpage was created using streamlit (source code can be found in `streamlit_app.py`). Here, we retrieved the data from our database using the pandas `read_sql()` function and a query. These queries are then used to create a visualization which ranges from barplots and scorigami charts to a nice interactive table where the user can order the rows based on any column.

The page should be available at https://share.streamlit.io/vvkgopalan/cpsc437_project.

To run the streamlit webpage locally, run `streamlit run streamlit_app.py` from the command line.
