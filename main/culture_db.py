import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

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

"## Query 1: Find all museums per borough"

sql_all_boroughs = "SELECT DISTINCT(borough) FROM culture.Location;"
try:
    boroughs = query_db(sql_all_boroughs)["borough"].tolist()
    borough = st.selectbox("Choose a customer", boroughs)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if borough:
	f"Display the result"

	sql_all_museums_per_borough = sql_order = f"""
        SELECT M.name, M.type
        FROM culture.Location L, culture.located_at_Museum M 
        WHERE L.borough = '{borough}'
        AND L.lid = M.lid;"""

	try:
		museums = query_db(sql_all_museums_per_borough)
		st.dataframe(museums)
	except:
		st.write("Sorry! Something went wrong with your query, please try again.")
