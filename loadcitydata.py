from app import create_server_connection, run_query_basic, run_query, Error
import datetime
import csv


def run_query_lumped(connection, query, values):
    cursor = connection.cursor(buffered = True)
    try:
        cursor.executemany(query, values)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")
    return cursor

connection = create_server_connection()
# cursor = run_query_basic(connection, """CREATE TEMPORARY TABLE temp_table (
#     city varchar(40) DEFAULT NULL,
#     state_id varchar(2) DEFAULT NULL,
#     lat varchar(5) DEFAULT NULL,
#     lng varchar(5) DEFAULT NULL
# );""")
# cursor = run_query_basic(connection, """LOAD DATA LOCAL INFILE '/uscities.csv'
# INTO TABLE temp_table
# FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
# LINES TERMINATED BY '\n'
# IGNORE 1 ROWS
# (city, state_id, lat, lng);""")

# cursor = run_query_basic(connection, """INSERT INTO citydata SELECT * FROM temp_table;""")
cities = []
states = []
lats = []
lngs = []
with open('uscities.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        cities.append(row[0])
        states.append(row[2])
        lats.append(row[6])
        lngs.append(row[7])
        # cursor = run_query(connection, "INSERT INTO citydata (city, state_id, lat, lng) VALUES (%s, %s, %s, %s);", (row[0], row[2], row[6], row[7]))
values = list(zip(cities, states, lats, lngs))
cursor = run_query_lumped(connection, "INSERT INTO citydata (city, state_id, lat, lng) VALUES (%s, %s, %s, %s);", values)


