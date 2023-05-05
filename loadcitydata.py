from app import create_server_connection, run_query_basic, run_query
import datetime
import csv

connection = create_server_connection()
with open('uscities.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        cursor = run_query(connection, "INSERT INTO citydata (city, state_id, lat, lng) VALUES (%s, %s, %s, %s);", (row[0], row[2], row[6], row[7]))

