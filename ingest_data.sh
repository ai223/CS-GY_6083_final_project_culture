echo "Refreshing tables..."
psql -d ai1221_db -f /home/ai1221/main/create_db.sql

echo "Loading all data..."
cat ./filmdirector.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.filmdirector FROM STDIN CSV HEADER"
cat ./has_director_Film.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.has_director_Film FROM STDIN CSV HEADER"
cat ./FilmScreenWriter.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.filmscreenwriter FROM STDIN CSV HEADER"
cat ./has_screenwriter.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.has_screenwriter FROM STDIN CSV HEADER"
cat ./FilmActor.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.filmactor FROM STDIN CSV HEADER"
cat ./has_actor.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.has_actor FROM STDIN CSV HEADER"
cat ./Location.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.location FROM STDIN CSV HEADER"
