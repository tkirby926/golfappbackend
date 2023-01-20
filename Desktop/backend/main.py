import create_app
from views import create_server_connection, run_query, getThreeWeeks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import flask
import datetime
import threading
import time
import schedule

# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()

def job():
    print("hi")
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT * FROM COURSES;")
    courses = cursor.fetchall()
    three_weeks = getThreeWeeks()
    for i in courses:
        cursor = run_query(connection, "SELECT * FROM TEETIMESCHEDULE WHERE course_id = '" + str(i[0]) + "' AND days ='" + str(datetime.datetime.today().weekday()) + "';")
        sched = cursor.fetchall()
        for j in sched:
            cursor = run_query(connection, "INSERT INTO TEETIMES (uniqid, teetime, cost, spots) VALUES ('" + str(i[0]) + "', '" + str(three_weeks) + " " + str(j[2]) + "', '" + str(j[3]) + "', 4);")
    context = {'message': 'completed nightly batch'}


app = create_app()
if __name__ == '__main__':
    # scheduler = BackgroundScheduler(daemon=False)
    # scheduler.start()
    # trigger = CronTrigger(
    #     year="*", month="*", day="*", hour="3", minute="0", second="0"
    # )
    # scheduler.add_job(func=job, trigger=trigger)
    app.run(debug=True)
    # while True:
    #     time.sleep(1)
    # schedule.every(15).seconds.do(run_threaded, update_times)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1) 


