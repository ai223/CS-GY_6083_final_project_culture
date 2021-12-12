import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
import datetime
import time
from dateutil.relativedelta import relativedelta

"#New York City Culture Finder/Event Planner/ NYC Art Nerds Lookup"


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


"## Query 1: Find all museums per borough with their number of special exhibitions over the past year"

sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
try:
    boroughs = query_db(sql_all_boroughs)["borough"].tolist()
    borough = st.selectbox("Choose a borough", boroughs,1)
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


"""## Query 4:Find all theaters playing a film starring(PICK YOUR ACTOR), playing in(PICK YOUR BOROUGH),
		Along with the name of the film, and showtime information, including room number
		and ticket price"""

sql_all_actors = "SELECT name FROM culture.FilmActor;"
sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
try:
	actors = query_db(sql_all_actors)["name"].tolist()
	actor = st.selectbox("Choose an Actor", actors)
	boroughs = query_db(sql_all_boroughs)["borough"].tolist()
	borough2 = st.selectbox("Choose a borough", boroughs,2)
except:
	st.write("Sorry! Something went wrong with your query, please try again.")


if actor and borough:
	f"Display the result"
	sql_actor_and_borough = f"""
		SELECT FT.name Theatre,F.name Title, FS.starttime dateAndTime, FS.roomNum, FT.ticketPrice TicketPrice
		FROM culture.has_location_FilmTheater FT,  
		culture.has_actor HA, culture.FilmActor FA,
		culture.has_director_Film F,culture.showing_at SA,culture.Location L,culture.FilmScreening FS
		WHERE FA.name = '{actor}'
		AND FA.faid = HA.faid
		AND HA.fid = F.fid
		AND F.fid = SA.fid
		AND SA.ftid= FT.ftid
		AND SA.fsid = FS.fsid
		AND FT.lid = L.lid
		AND L.borough = '{borough2}'"""

	try:
		actorborough = query_db(sql_actor_and_borough)
		st.dataframe(actorborough)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")


"""## Query 5: Find all international movies, by THIS DIRECTOR, and THIS GENRE that are playing in THIS BOROUGH"""

sql_all_directors = "SELECT name FROM culture.filmdirector;"
sql_all_genres = "SELECT DISTINCT(genre) FROM culture.has_director_Film;"
sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
try:
	directors= query_db(sql_all_directors)["name"].tolist()
	director = st.selectbox("Choose a Director", directors)
	genres = query_db(sql_all_genres)["genre"].tolist()
	genre = st.selectbox("Choose a genre!", genres)
	boroughs = query_db(sql_all_boroughs)["borough"].tolist()
	borough3 = st.selectbox("Choose a borough", boroughs,3)
except:
	st.write("Sorry! Something went wrong with your query, please try again.")


if director and genre and borough3:
	f"Display the result"
	sql_director_and_borough_and_genre = f"""
		SELECT FT.name Theatre,F.name Title, FS.starttime dateAndTime, FS.roomNum, FT.ticketPrice TicketPrice
		FROM culture.has_location_FilmTheater FT,  
		culture.filmdirectpr FD,
		culture.has_director_Film F,culture.showing_at SA,culture.Location L,culture.FilmScreening FS
		WHERE FD.name = '{director}'
		AND FD.fdid = F.fdid
		AND F.fid = SA.fid
		AND SA.ftid= FT.ftid
		AND SA.fsid = FS.fsid
		AND FT.lid = L.lid
		AND L.borough = '{borough2}'
		AND F.genre = '{genre};'"""

	try:
		directorboroughgenre = query_db(sql_director_and_borough_and_genre)
		st.dataframe(directorboroughgenre)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")





"""## Query 6: Find all ACTOR/Director Teams, and count how many moviess they did together. For the 
purpose of this query, we are going to consider an Actor/Director team,
as an Actor and Director who worked on 2 or more movies together. """




"""## Query 7: PLAN YOUR DAY in NYC. Pick a day, and we will tell you what Films are Playing on that day, and pair that with an exhibit that is happening at a Museum on the same day!"""

sql_all_days = "SELECT CAST(starttime AS DATE) FROM culture.FilmScreening;"
try:
	days = query_db(sql_all_days)["starttime"].tolist()
	day = st.selectbox("Choose a day!", days)

except:
	st.write("Sorry! Something went wrong with your query, please try againnnnnnnn.")


if day:
	f"Display the result"

	sql_film_and_exhibit = f"""
	SELECT FT.name theater, F.name film, 
	       FS.starttime, FS.roomnum theatre_room,
	       LAM.name museum, ME.name exhibit,
	       L1.borough
	FROM culture.has_location_FilmTheater FT,
	     culture.showing_at SA,
	     culture.has_director_Film F,
	     culture.FilmScreening FS,
	     culture.MuseumEvent ME,
	     culture.has_event HE,
	     culture.located_at_Museum LAM,
	     culture.Location L1, 
	     culture.Location L2
	WHERE FT.ftid = SA.ftid
	AND F.fid = SA.fid
	AND SA.fsid = FS.fsid
	AND CAST(FS.starttime AS DATE) = '{day}'
	AND '{day}' >= ME.startDate
	AND '{day}' <= ME.endDate
	AND ME.meid = HE.meid
	AND HE.mid = LAM.mid
	AND FT.lid = L1.lid
	AND LAM.lid = L2.lid
	AND L1.borough = L2.borough;"""
	
	try:
		dayout = query_db(sql_film_and_exhibit)
		st.dataframe(dayout)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")





   


