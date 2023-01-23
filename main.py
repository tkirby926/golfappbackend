from __init__ import create_app
from golfappbackend.views import create_server_connection, run_query, getThreeWeeks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import flask
import datetime
import threading
import time

# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()


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


