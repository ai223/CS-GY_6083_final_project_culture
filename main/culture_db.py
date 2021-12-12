import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
import datetime
import time
from dateutil.relativedelta import relativedelta

"# Demo: Streamlit + Postgres"


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df


"## Read tables"

sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
try:
    all_table_names = query_db(sql_all_table_names)["relname"].tolist()
    table_name = st.selectbox("Choose a table", all_table_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if table_name:
    f"Display the table"

    sql_table = f"SELECT * FROM culture.{table_name};"
    try:
        df = query_db(sql_table)
        st.dataframe(df)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

"""## Query 4:Find all theaters playing a film starring(PICK YOUR ACTOR), playing in(PICK YOUR BOROUGH)
Just putting this query here too test some error i got before"""

sql_all_actors = "SELECT DISTINCT(name) FROM culture.FilmActor;"
actors = query_db(sql_all_actors)["name"].tolist()
actor = st.selectbox("Choose an Actor", actors)

sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
boroughs = query_db(sql_all_boroughs)["borough"].tolist()
borough = st.selectbox("Choose a borough", boroughs)


if borough and actor:
	f"Display the result"
	sql_actor_and_borough = f"""
		SELECT FT.name
		FROM has_location_FilmTheater FT, Location L, 
		has_actor HA,FilmActor FA,
		has_director_Film F,showing_at SA
		WHERE faid.FA = faid.HA
		AND fid.HA = fid.F
		AND fid.F = fid.SA
		AND ftid.SA = FT.ftid
		AND FT.lid = L.lid
		AND L.borough = {borough}
		AND FA.name = {actor};"""

	try:
		actorborough = query_db(sql_actor_and_borough)
		st.dataframe(actorborough)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")


"## Query 1: Find all museums per borough with their number of special exhibitions over the past year"

sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
try:
    boroughs = query_db(sql_all_boroughs)["borough"].tolist()
    borough = st.selectbox("Choose a borough", boroughs)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if borough:
	f"Display the result"

	todays_Date = datetime.date.fromtimestamp(time.time()) - relativedelta(years=1)
	date_in_ISOFormat = todays_Date.isoformat()

	sql_all_museums_per_borough = sql_order = f"""
        SELECT M.name museum, M.type, COUNT(ME.meid) exhibitions
        FROM culture.Location L, culture.located_at_Museum M, culture.has_event E
        LEFT JOIN culture.MuseumEvent ME ON (ME.meid = E.meid AND ME.startDate >= '{date_in_ISOFormat}'::date)
        WHERE L.borough = '{borough}'
        AND M.lid = L.lid
        AND E.mid = M.mid
        GROUP BY M.name, M.type
        ORDER BY museum, type, exhibitions;"""

	try:
		museums = query_db(sql_all_museums_per_borough)
		st.dataframe(museums)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")

f"""## Query 2: Find all museums in which an artists work appears, 
       along with the number of works and their average, as well as the earliest 
       and latest dates their work appears"""

sql_all_creators = "SELECT name FROM culture.MuseumObjectCreator ORDER BY name;"
try:
    creators = query_db(sql_all_creators)["name"].tolist()
    creator = st.selectbox("Choose an artist or creator", creators)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if creator:
	f"Display the result"

	sql_all_museums_by_creator = f"""
		SELECT M.name museum, 
		       COUNT(MO.moid) total_objects, 
			   AVG(MO.popularityRank)::numeric(10, 1) average_popularity,
			   MIN(MO.date) earliest_piece,
			   MAX(MO.date) latest_piece
		FROM culture.MuseumObjectCreator C, 
		     culture.created_by CB,
		     culture.has_object_MuseumObject MO,
		     culture.located_at_Museum M
		WHERE C.name = '{creator}'
		AND C.mocid = CB.mocid
		AND CB.moid = MO.moid
		AND MO.mid = M.mid
		GROUP BY (M.name)
		ORDER BY total_objects DESC, museum;"""

	try:
		museums_by_artist = query_db(sql_all_museums_by_creator)
		st.dataframe(museums_by_artist)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")

f"""## Query 3: Allow a user to search for artworks starting with the search term displaying the piece, the creator of the piece, the museum where it can be found and other data"""

artwork_stem = st.text_input('Input your sentence here:') 

if artwork_stem:
	f"Display the result"

	sql_find_artworks_by_name = f"""
		SELECT MO.name piece, MOC.name artist, MO.type, MO.style, 
		       MO.date, MO.country, MO.popularityRank, M.name museum,
		       L.borough
		FROM culture.has_object_MuseumObject MO,
		     culture.MuseumObjectCreator MOC,
		     culture.created_by CB,
		     culture.located_at_Museum M,
		     culture.Location L
		WHERE MO.name LIKE '{artwork_stem}%'
		AND MO.moid = CB.moid
		AND CB.mocid = MOC.mocid
		AND MO.mid = M.mid
		AND M.lid = L.lid
		ORDER BY piece;"""

	try:
		matching_artworks = query_db(sql_find_artworks_by_name)
		st.dataframe(matching_artworks)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")

##"## Query4: Find all theaters playing a movie by THIS ACTOR, by THIS GENRE, and In This BOROUGH"


"""## Query 4:Find all theaters playing a film starring(PICK YOUR ACTOR), playing in(PICK YOUR BOROUGH)"""
'''
sql_all_actors = "SELECT DISTINCT(name) FROM culture.FilmActor;"
actors = query_db(sql_all_actors)["name"].tolist()
actor = st.selectbox("Choose an Actor", actors)

sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
boroughs = query_db(sql_all_boroughs)["borough"].tolist()
borough = st.selectbox("Choose a borough", boroughs)


if borough and actor:
	f"Display the result"
	sql_actor_and_borough = f"""
		SELECT FT.name
		FROM has_location_FilmTheater FT, Location L, 
		has_actor HA,FilmActor FA,
		has_director_Film F,showing_at SA
		WHERE faid.FA = faid.HA
		AND fid.HA = fid.F
		AND fid.F = fid.SA
		AND ftid.SA = FT.ftid
		AND FT.lid = L.lid
		AND L.borough = {borough}
		AND FA.name = {actor};"""

	try:
		actorborough = query_db(sql_actor_and_borough)
		st.dataframe(actorborough)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")
'''


"""## Query 5: Find all international movies, by THIS DIRECTOR that are playing in THIS BOROUGH"""



