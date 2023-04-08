from app import create_server_connection, run_query_basic, run_query
import datetime

print("hi")
connection = create_server_connection()
today = datetime.datetime.today()
day_of_week = today.weekday()
four_weeks = today + datetime.timedelta(weeks=4)
cursor = run_query_basic(connection, "SELECT * FROM TEETIMESCHEDULE WHERE days ='" + str(day_of_week) + "';")
sched = cursor.fetchall()
for j in sched:
    hours = j[2].seconds//3600
    minutes = (j[2].seconds//60)%60
    right_time = four_weeks.replace(hour=int(hours), minute=int(minutes), second=0)
    cursor = run_query(connection, "INSERT INTO TEETIMES (uniqid, teetime, cost, spots, cart) VALUES (%s, %s, %s, 4, 0);", (str(j[0]), str(right_time), str(j[3])))
context = {'message': 'completed nightly batch'}