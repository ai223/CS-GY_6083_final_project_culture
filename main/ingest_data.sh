cat ./filmdirector.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.filmdirector FROM STDIN CSV HEADER"
cat ./has_director_Film.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.has_director_Film FROM STDIN CSV HEADER"
