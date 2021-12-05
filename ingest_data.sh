cat ./filmdirector.csv | psql -U ai1221 -d ai1221_db -c "COPY culture.filmdirector FROM STDIN CSV HEADER"
