
from audioop import reverse
from crypt import methods
from email.policy import default
from os import curdir
from re import I
from flask import Blueprint, render_template, request
import flask
from importlib_metadata import re
import mysql.connector
from mysql.connector import Error
from numpy import mat
import pandas as pd
import pgeocode
from haversine import haversine, Unit
import random
from PIL import Image
import json
import base64
import requests
import io
import uuid
import hashlib
import stripe
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import dropbox
import boto3
import random, string


BUCKET = 'golftribephotos'
s3 = boto3.client('s3', aws_access_key_id="AKIAT6ACDNJMUUI2VXPR", aws_secret_access_key= "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")

def job2():
    return
    # connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    # cursor = run_query(connection, "DELETE FROM TEETIMES WHERE teetime > CURRENT_TIMESTAMP")

def job():
    print("hi")
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
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

# refresh_token = "3Zn9qMSYVyAAAAAAAAAAAVPUsKUA33XATk-8tKujM1V8q0WcihZevxGE5x46ZZF5"
# app_key = "oop5bqdljvyo2aa"
# app_secret = "hsspgilce6up444"
# dbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret)
imgbbkey = '5acb680159cbebee2e67690c18137e89'
trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="*", second=5
)
# trigger2 = CronTrigger(
#         year="*", month="*", day="*", hour="*", minute="*", second=0
# )
scheduler = BackgroundScheduler(daemon=False)
scheduler.start()
scheduler.add_job(func=job, trigger=trigger)
# scheduler.add_job(func=job2, trigger=trigger2)

def create_server_connection(host_name, user_name, user_password, db):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database = db
        )
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def run_query(connection, query, variables):
    cursor = connection.cursor(buffered = True)
    try:
        cursor.execute(query, variables)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")
    return cursor

def run_query_basic(connection, query):
    cursor = connection.cursor(buffered = True)
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")
    return cursor

def location_search_helper(loc):
    nomi = pgeocode.Nominatim('us')
    query = nomi.query_postal_code(loc)

    data = {
        "lat": str(query["latitude"]),
        "lon": str(query["longitude"])
    }
    return data['lat'], data['lon']

def user_helper(connection, user):
    if user is None or user == 'null':
        return 'null'
    cursor = run_query(connection, "SELECT username FROM COOKIES WHERE sessionid = %s;", (user,))
    username = cursor.fetchone()
    if username is None:
        return False
    username = list(username)
    return username[0]

# def admin_helper(connection, user):
#     if user is None or user == 'null':
#         return 'null'
#     cursor = run_query(connection, "SELECT username FROM COOKIES WHERE sessionid = '" + user + "' AND user = '2';")
#     username = cursor.fetchone()
#     if username is None:
#         return False
#     username = list(username)
#     return username[0]

def make_cookie(user, type):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM COOKIES WHERE sessionid = %s;", (x, ))
    collision = cursor.fetchone()[0]
    print(user)
    print(type)
    print('pooooop')
    while collision > 0:
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
        cursor = run_query(connection, "SELECT COUNT(*) FROM COOKIES WHERE sessionid = %s;", (x, ))
        collision = cursor.fetchone()[0]
    cursor = run_query(connection, "INSERT INTO COOKIES (username, sessionid, user) VALUES (%s, %s, %s);", (user, x, type))
    print('johhnyy')
    return x

def set_verification(user):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM EMAILVERIF WHERE emailcode = %s;", (x, ))
    collision = cursor.fetchone()[0]
    while collision > 0:
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
        cursor = run_query(connection, "SELECT COUNT(*) FROM COOKIES WHERE sessionid = %s;", (x, ))
        collision = cursor.fetchone()[0]
    cursor = run_query(connection, "INSERT INTO EMAILVERIF (username, emailcode) VALUES (%s, %s);", (user, x))
    return x

def translate_verification(connection, user):
    if user is None or user == 'null':
        return 'null'
    cursor = run_query(connection, "SELECT username FROM EMAILVERIF WHERE emailcode = %s;", (user, ))
    username = cursor.fetchone()
    if username is None:
        return False
    username = list(username)
    return username[0]


views = Blueprint('views', __name__)

# @views.route('/')
# def home():
#     # connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     # run_query(connection, """CREATE TABLE Friendships (UserId1 VARCHAR(20), UserId2 VARCHAR(20));""")
#     if flask.session.get('username'):
#         context = {'profile_link': '/user/' + flask.session['username'], 'username': flask.session['username']}
#     else:
#         context = {'profile_link': None, 'username': None}
    
#     return render_template('initial_page.html', **context)

# @views.route('/swiper/')
# def show_profiles():
#     context = {"good_times": [], "is_selected": 10, "zip": ''}
#     return render_template('tindersearch.html')

# @views.route('/times/')
# def show_times():
#     context = {"good_courses": [], "is_selected": 10, "zip": ''}
#     return render_template('teetimesearch.html')

# @views.route('/login/')
# def login():
#     context = {"showfail": "no"}
#     return render_template('login_page.html', **context)

# @views.route('/test_login/')
# def test_login():
#     connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     cursor = run_query(connection, "SELECT * FROM USERS WHERE username='" 
#               + flask.request.args.get('username') + "' AND password='" + flask.request.args.get('password') + "'")
#     attempt = cursor.fetchone()
#     if attempt is None:
#         context = {"showfail": "yes"}
#         return render_template('login_page.html', **context)
#     else:
#         flask.session['username'] = flask.request.args.get('username')
#         return flask.redirect(flask.url_for('views.home'))

# @views.route('/create_account/')
# def create_account():
#     return render_template('create_account.html')

# @views.route('/render_account/', methods = ["POST"])
# def render_account():
#     connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     # # print(flask.request.form.get('username'))
#     # # print(flask.request.args.get('password'))
#     # # print(flask.request.args.get('fullname'))
#     # x = "INSERT INTO USERS (username, firstname, lastname, password, email, filename, drinking, score, playstyle, descript, college) VALUES (" + flask.request.form.get('username') + ", " + flask.request.form.get('firstname') + ", " 
#     # + flask.request.form.get('lastname') + ", " + flask.request.form.get('password') + ", " + flask.request.form.get('email') + ", " + flask.request.form.get('filename') + ", " + flask.request.form.get('drinking') + ", " + flask.request.form.get('score') + ", " 
#     # + flask.request.form.get('playstyle') + ", " + flask.request.form.get('descript') + ", " + flask.request.form.get('college') + ")"
#     # print(x)
#     # cursor = run_query(connection, """INSERT INTO USERS (username, fullname, password,
#     #                                 email, filename, drinking, score, playstyle, descript, college) VALUES ('""" +
#     #                                 flask.request.form.get('username') + "', '" + flask.request.form.get('firstname') + "', '" + flask.request.form.get('lastname') + "', '" +
#     #                                 flask.request.form.get('password') + "', '" + flask.request.form.get('email') + "', '" +
#     #                                 flask.request.form.get('filename') + "', '" + flask.request.form.get('drinking') + "', '" +
#     #                                 flask.request.form.get('score') + "', '" + flask.request.form.get('playstyle') + "', '" +
#     #                                 flask.request.form.get('descript') + "', '" + flask.request.form.get('college') + "')")
#     # return render_template("initial_page.html")

# @views.route('/logout/')
# def logout():
#     flask.session.pop('username', None)
#     return flask.redirect(flask.url_for('views.home'))

# @views.route('/render_loc/')
# def render_loc():
#     # print(data)
#     # connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     # cursor = run_query(connection, "SELECT * FROM COURSES")
#     # if (data['lat'] > 0 and data['lon'] > 0):
#     #     cursor = run_query(connection, "SELECT * FROM COURSES WHERE SQRT(POWER(DIFFERENCE(latitude, " + str(data['lat']) + "), 2)" + 
#     #                                    " + POWER(DIFFERENCE(longitude," + str(data['lon']) + "), 2)) < 2;")
#     # elif (data['lat'] < 0 and data['lon'] > 0):
#     #     data['lat'] = abs(data['lat'])
#     #     cursor = run_query(connection, "SELECT * FROM COURSES WHERE SQRT(POWER(SUM(latitude, " + str(data['lat']) + "), 2)" + 
#     #                                    " + POWER(DIFFERENCE(longitude, " + str(data['lon']) + "), 2)) < 2;")
#     # elif (data['lat'] > 0 and data['lon'] < 0):
#     #     data['lon'] = abs(data['lon'])
#     #     x = "SELECT * FROM COURSES WHERE SQRT(SUM(POWER(DIFFERENCE(latitude, " + str(data['lat']) + "), 2)" + ", POWER(SUM(longitude, " + str(data['lon']) + "), 2))) < 2;"
#     #     print(x)
#     #     cursor = run_query(connection, "SELECT * FROM COURSES WHERE SQRT(SUM(POWER(DIFFERENCE(latitude, " + str(data['lat']) + "), 2)" + 
#     #                                    ", POWER(SUM(longitude, " + str(data['lon']) + "), 2))) < 2;")
#     # else:
#     #     cursor = run_query(connection, "SELECT * FROM COURSES WHERE SQRT(POWER(SUM(latitude, " + str(data['lat']) + "), 2)" + 
#     #                                    " + POWER(SUM(longitude, " + str(data['lon']) + "), 2)) < 2;")
#     course_list, lat, lon = location_search_helper(flask.request.args.get('loc'), flask.request.args.get('length'))
#     good_courses = []
#     for i in course_list:
#         coord1 = (float(i[2]), float(i[3]))
#         coord2 = (lat, lon)
#         print(haversine(coord1, coord2))
#         if (haversine(coord1, coord2)/1.609344 < float(flask.request.args.get('length'))):
#             good_courses.append([i[0], i[1], i[4]])
#     context = {"good_courses": good_courses, "is_selected": flask.request.args.get('length'), "zip": flask.request.args.get('loc')}
#     return render_template('teetimesearch.html', **context)

@views.route("""/api/v1/<int:zip_url_slug>&<int:length_url_slug>&<string:firstdate_url_slug>&<string:firsttime_url_slug>
                &<string:seconddate_url_slug>&<string:secondtime_url_slug>""")
def swiper_api(zip_url_slug, length_url_slug, firstdate_url_slug, firsttime_url_slug, 
               seconddate_url_slug, secondtime_url_slug):
    course_list, lat, lon = location_search_helper(zip_url_slug, length_url_slug)
    good_courses = []
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    for i in course_list:
        coord1 = (float(i[2]), float(i[3]))
        coord2 = (lat, lon)
        print(haversine(coord1, coord2))
        if (haversine(coord1, coord2)/1.609344 < float(length_url_slug)):
            good_courses.append([i[0], i[1], i[4]])
            cursor = run_query(connection, """SELECT T.timeid, T.teetime, T.cost FROM TEETIMES T, BOOKEDTIMES B, COURSES C, USERS U WHERE
                                              B.timeid = T.timeid AND T.uniqid = """ + i[0] + " AND T.")
    context = {'good': firsttime_url_slug, 'bad': 'no'}
    return flask.jsonify(**context)


@views.route('/api/v1/locations/<string:zip>/<int:length>')
def get_times(zip, length):
    print(zip)
    course_list, lat, lon = location_search_helper(zip, length)
    good_courses = []
    for i in course_list:
        coord1 = (float(i[2]), float(i[3]))
        coord2 = (lat, lon)
        print(haversine(coord1, coord2))
        if (haversine(coord1, coord2)/1.609344 < float(length)):
            good_courses.append([i[0], i[1], i[4]])
    context = {"good_courses": good_courses}
    return flask.jsonify(**context)

@views.route('/api/v1/search/<string:search>/<string:user>')
def get_search_results(search, user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    print(user)
    search = search + '%'
    cursor = run_query(connection, "SELECT username, firstname, lastname, imageurl FROM USERS WHERE username != %s AND (username LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR CONCAT(firstname, ' ', lastname) LIKE %s) LIMIT 6;", (user, search, search, search, search))
    results = cursor.fetchall()
    files = []
    #file = dbx.files_get_thumbnail("/Apps/GolfTribe/User_Profile_Pictures/lgldslag.jpeg")
    # file = dbx.files_get_thumbnail("/Apps/GolfTribe/User_Profile_Pictures/lgldslag.jpeg")
    #files.append(s3.get_object(Bucket=BUCKET, Key="helloworld2"))
    search = '%' + search
    if len(results) < 6:
        cursor = run_query(connection, "SELECT CONCAT('/course/', uniqid) AS url, coursename FROM COURSES WHERE coursename LIKE %s LIMIT 6;", (search, ))
        results1 = cursor.fetchall()
        results = results + results1
    print(results)
    context = {"results": results} 
    return flask.jsonify(**context)

@views.route('/api/v1/search/users_friends/<string:user>/<string:search>/<string:page>/<string:limit>')
def get_search_users(user, search, page, limit):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    search = search + '%'
    cursor = run_query(connection, "SELECT username, firstname, lastname, imageurl FROM USERS U, Friendships F WHERE ((F.userid1 = U.username AND F.userid2 = %s) OR (F.userid1 = %s AND F.userid2 = U.username)) AND (U.username LIKE %s OR U.firstname LIKE %s OR U.lastname LIKE %s OR CONCAT(U.firstname, ' ', U.lastname) LIKE %s) LIMIT %s OFFSET %s;", (user, user, search, search, search, search, int(limit) + 1, int(page)*int(limit)))
    friends = cursor.fetchall()
    index = len(friends)
    if (index == int(limit)):
        context = {"results": friends, "last": True, "index": limit}
        return flask.jsonify(**context)
    if (index == int(limit) + 1):
        context = {"results": friends, "last": False, "index": limit}
        return flask.jsonify(**context)
    cursor = run_query(connection, "SELECT COUNT(*) FROM USERS U, Friendships F WHERE ((F.userid1 = U.username AND F.userid2 = %s) OR (F.userid1 = %s AND F.userid2 = U.username));", (user, user))
    total_friends = cursor.fetchone()[0]
    cursor = run_query(connection, "SELECT username, firstname, lastname, imageurl FROM USERS WHERE (username LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR CONCAT(firstname, ' ', lastname) LIKE %s) AND username != %s AND username NOT IN (SELECT U.username FROM USERS U, Friendships F WHERE ((F.userid1 = U.username AND F.userid2 = %s) OR (F.userid1 = %s AND F.userid2 = U.username))) LIMIT %s OFFSET %s;", (search, search, search, search, user, user, user, int(limit) + 1 - index, max((int(page)*int(limit)) - total_friends, 0)))
    users = cursor.fetchall()
    results = friends + users
    results = list(results)
    more = False
    if len(results) == int(limit) + 1:
        more = True
        results.pop()
    context = {"results": results, "more": more, "index": index} 
    return flask.jsonify(**context)

@views.route('/api/v1/check_cookie/<string:cookie>')
def get_cookie(cookie):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT username FROM COOKIES WHERE sessionid = %s;", (cookie, ))
    user = list(cursor.fetchone())
    context = {'username': 'null'}
    if (len(user) != 0):
        context = {'username': user[0]}
    return flask.jsonify(**context)

@views.route('/api/v1/delete_cookie/<string:cookie>', methods=["DELETE"])
def delete_cookie(cookie):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "DELETE FROM COOKIES WHERE sessionid = %s;", (cookie, ))
    context = {'message': 'success'}
    return flask.jsonify(**context)

@views.route('/api/v1/send_message', methods = ["POST"])
def send_message():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, req['user1'])
    cursor = run_query(connection, "INSERT INTO Messages (content, userid1, userid2, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", (req['message'], user, req['user2']))
    cursor = run_query(connection, "UPDATE USERS SET notifications = notifications + 1 WHERE username = %s;", (req['user2'], ))
    message = ""
    context = {'error': message}
    return flask.jsonify(**context)

@views.route('/api/v1/search/upd/<string:user>')
def get_search_friends(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT username, firstname, lastname, imageurl FROM USERS U, Friendships F WHERE ((F.userid2 = %s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)) LIMIT 8;", (user, user))
    results = cursor.fetchall()
    index = len(results)
    cursor = run_query(connection, "SELECT username, firstname, lastname, imageurl FROM USERS U ORDER BY RAND() LIMIT %s;", (8 - len(results), ))
    rest = cursor.fetchall()
    results = results + rest
    requests = get_friend_requests_helper(connection, user, '0')
    good_user_times, friends_in_time = get_friends_times_helper(connection, user)
    context = {"results": results, 'index': index, 'requests': requests, 'good_user_times': good_user_times, 'user_friends': friends_in_time} 
    return flask.jsonify(**context)

@views.route('/api/v1/search/only_friends/<string:user>/<string:search>/<string:page>')
def get_only_friends(user, search, page):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    search = search + '%'
    cursor = run_query(connection, "SELECT username, firstname, lastname FROM USERS U, Friendships F WHERE ((F.userid1 = U.username AND F.userid2 = %s) OR (F.userid1 = %s AND F.userid2 = U.username)) AND (U.username LIKE %s OR U.firstname LIKE " + 
    "%s OR U.lastname LIKE %s OR CONCAT(U.firstname, ' ', U.lastname) LIKE %s) LIMIT 4 OFFSET %s;", (user, user, search, search, search, search, int(page)*3))
    results = cursor.fetchall()
    context = {"results": results} 
    return flask.jsonify(**context)

@views.route('/api/v1/send_invite')
def send_invites():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    for i in req:
        print('hello')
        #send automated email to friends in request list
        # cursor = run_query(connection, "SELECT username, firstname, lastname FROM USERS U, Friendships F WHERE ((F.userid1 = U.username AND F.userid2 = '" + user + "') OR (F.userid1 = '" + user + "' AND F.userid2 = U.username)) AND (U.username LIKE '" + search + "%' OR U.firstname LIKE '"
    context = {'error': 'none'}
    return flask.jsonify(**context)
    

@views.route('/api/v1/in_time/<string:user>/<string:timeid>')
def check_in_time(user, timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT T.teetime, C.Coursename, T.Cost, T.Spots FROM BOOKEDTIMES B, COURSES C, TEETIMES T WHERE B.username = %s AND B.timeid = %s AND C.uniqid = T.uniqid AND T.timeid = B.timeid;", (user, timeid))
    in_time = True
    time_info = cursor.fetchone()
    print(time_info)
    if len(time_info) == 0:
        in_time = False
    context = {"time_info": time_info, "in_time": in_time} 
    return flask.jsonify(**context)

@views.route('/api/v1/notifications/<string:user>')
def get_notifications(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    username = user_helper(connection, user)
    cursor = run_query(connection, "SELECT notifications, imageurl FROM USERS WHERE username = %s;", (username, ))
    data = cursor.fetchone()
    notifications = data[0]
    imageurl = data[1]
    context = {'notifications': notifications, 'imgurl': imageurl}
    return flask.jsonify(**context)

@views.route('/api/v1/booked_times/<string:user>')
def get_booked_times(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT T.timeid, C.Coursename, T.teetime FROM Courses C, Teetimes T, Bookedtimes B WHERE B.timeid = T.timeid AND C.uniqid = T.uniqid AND B.username = %s ORDER BY teetime;", (user, ))
    times_booked = cursor.fetchall()
    context = {'times_booked': times_booked}
    return flask.jsonify(**context)

@views.route('/api/v1/add_review', methods=["POST"])
def post_review():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, req['user'])
    cursor = run_query(connection, "INSERT INTO Reviews (username, content, rating, timestamp) VALUES (%s, '%s, %s, CURRENT_TIMESTAMP);", (user, req["description"], req["rating"]))
    context = {'error': 'none'}
    return flask.jsonify(**context)

@views.route('/api/v1/add_course_review', methods=["POST"])
def post_course_review():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, req['user'])
    cursor = run_query(connection, "INSERT INTO CourseReviews (username, description, rating, timestamp, uniqid) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s);", (user, req["description"], req["rating"], req['courseid']))
    context = {'error': 'none', 'user_readable': user}
    return flask.jsonify(**context)

@views.route('/api/v1/post_post', methods=["POST"])
def post_post():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, req['user'])
    cursor = run_query(connection, "INSERT INTO POSTS (content, username, timestamp, link) VALUES (%s, %s, CURRENT_TIMESTAMP, %s);", (req['content'], user, req['link']))
    cursor = run_query(connection, "SELECT CURRENT_TIMESTAMP;")
    context = {'error': 'none', 'curtime': cursor.fetchone()}
    return flask.jsonify(**context)

def get_friend_requests_helper(connection, user, page):
    cursor = run_query(connection, "UPDATE USERS SET notifications = 0 WHERE username = %s;", (user, ))
    cursor = run_query(connection, "SELECT R.username1, U.firstname, lastname FROM REQUESTEDFRIENDS R, USERS U WHERE R.username2 = %s AND R.username1 = U.username LIMIT 6 OFFSET %s;", (user, int(page)*5))
    results = cursor.fetchall()
    return results

@views.route('/api/v1/friend_requests/<string:user>/<string:page>')
def get_friend_requests(user, page):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    results = get_friend_requests_helper(connection, user, page)
    context = {"results": results} 
    return flask.jsonify(**context)

@views.route('/api/v1/search/courses/<string:search>/<string:page>/<string:limit>')
def get_search_courses(search, page, limit):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    search = '%' + search + '%'
    cursor = run_query(connection, "SELECT CONCAT('/course/', uniqid) AS url, coursename, imageurl FROM COURSES WHERE coursename LIKE "
    "%s LIMIT %s OFFSET %s;", (search, int(limit), int(page)*int(limit)))
    results = cursor.fetchall()
    last = False
    if len(results) < 20:
        last = True
    context = {"results": results, "last": last} 
    return flask.jsonify(**context)

@views.route('/api/v1/search/any_course/<string:limit>')
def get_some_courses(limit):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT uniqid, coursename FROM COURSES LIMIT %s;", (int(limit), ))
    results = cursor.fetchall()
    context = {"results": results, "last": True} 
    return flask.jsonify(**context)

@views.route('/api/v1/users/<string:user1>/<string:user2>')
def get_user_profile(user1, user2):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user1 = user_helper(connection, user1)
    cursor = run_query(connection, "SELECT username, firstname, lastname, drinking, score, playstyle, descript, college, imageurl FROM USERS WHERE username=%s;", (user2, ))
    user = cursor.fetchone()
    cursor = run_query(connection, "SELECT * from POSTS where username = %s ORDER BY timestamp DESC LIMIT 3;", (user2, ))
    posts = cursor.fetchall()
    cursor = run_query(connection, "SELECT C.coursename, T.teetime, T.cost, T.spots, T.timeid FROM Teetimes T, Courses C WHERE C.uniqid = T.uniqid AND T.timeid" + 
                                   " IN (SELECT timeid FROM BOOKEDTIMES WHERE username = %s);", (user2, ))
    tee_times = cursor.fetchall()
    friends_in_time = friends_in_time_helper(connection, tee_times, user1)
    more = True
    if (len(posts) != 3):
        more = False
    cursor = run_query(connection, "SELECT COUNT(*) FROM FRIENDSHIPS WHERE (userid1 = %s AND userid2 = %s) OR (userid2 = "
                                    "%s AND userid1 = %s)", (user1, user2, user1, user2))
    status = "f"
    count = cursor.fetchone()[0]
    print(count)
    if (count == 0):
        status = "p"
        cursor = run_query(connection, "SELECT COUNT(*) FROM REQUESTEDFRIENDS WHERE username1 = %s AND username2 = %s;", (user1, user2))
        if (cursor.fetchone()[0] == 0):
            cursor = run_query(connection, "SELECT COUNT(*) FROM REQUESTEDFRIENDS WHERE username1 = %s AND username2 = %s;", (user2, user1))
            status = "r"
            if (cursor.fetchone()[0] == 0):
                status = "n"
        
    context = {"user": user, "status": status, "posts": posts, "has_more_posts": more, 'tee_times': tee_times, 'friends_in_time': friends_in_time}
    return flask.jsonify(**context)

@views.route('/api/v1/teetimes/<string:zip>/<string:date>')
def get_swipe_times(zip, date):
    lat, lon = location_search_helper(zip)
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT *, SQRT(POWER((%s - latitude), 2) + POWER((%s - longitude), 2)) AS X FROM COURSES ORDER BY X LIMIT 5;", (lat, lon))
    good_courses = cursor.fetchall()
    good_times = []
    for i in good_courses:
        cursor = run_query(connection, "SELECT t.timeid, t.cost, c.coursename FROM TEETIMES t, COURSES c WHERE c.coursename=" +
                                        "%s AND c.uniqid = t.uniqid AND CAST(teetime AS DATE) = %s AND t.timeid IN (SELECT DISTINCT timeid FROM BOOKEDTIMES);", (i[4], date))
        good_times = cursor.fetchall()
        print(good_times)
        random.shuffle(good_times)
    print(good_courses)
    context = {'good_courses': good_courses, 'good_times': good_times}
    return flask.jsonify(**context)

@views.route('/api/v1/location_city/<string:lat>/<string:lon>/<string:date>')
def get_times_city(lat, lon, date):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT *, SQRT(POWER((%s - latitude), 2) + POWER((%s - longitude), 2)) AS X FROM COURSES ORDER BY X LIMIT 5;", (lat, lon))
    good_courses = cursor.fetchall()
    good_times = []
    for i in good_courses:
        cursor = run_query(connection, "SELECT t.timeid, t.cost, c.coursename FROM TEETIMES t, COURSES c WHERE c.coursename=" +
                                        "%s AND c.uniqid = t.uniqid AND CAST(teetime AS DATE) = %s AND t.timeid IN (SELECT DISTINCT timeid FROM BOOKEDTIMES);", (i[4], date))
        good_times = cursor.fetchall()
        print(good_times)
        random.shuffle(good_times)
    print(good_courses)
    context = {'good_courses': good_courses, 'good_times': good_times}
    return flask.jsonify(**context)

@views.route('/api/v1/posts/<string:user>/<int:page>')
def get_all_posts(user, page):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT * FROM Posts WHERE username = %s OR username IN (SELECT U.username FROM USERS U, Friendships F WHERE ((F.userid2 = " +
                                    "%s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2))) ORDER BY timestamp DESC LIMIT 6 OFFSET %s;", (user, user, user, page * 5))
    posts = cursor.fetchall()
    print('hello')
    more = False
    if (len(posts) == 6):
        more = True
    context = {'posts': posts, 'has_more_posts': more, 'user': user}
    return flask.jsonify(**context)

@views.route('/api/v1/email/<string:email>')
def check_email(email):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM USERS WHERE email = %s;", (email, ))
    is_account = cursor.fetchone()[0]
    context = {'is_account': is_account}
    return flask.jsonify(**context)

@views.route('/api/v1/course/tee_sheet/<string:courseid>/<string:date>')
def get_tee_sheet(courseid, date):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseid)
    cursor = run_query(connection, "SELECT teetime, timeid, cart FROM Teetimes WHERE CAST(teetime AS DATE) = %s AND uniqid = %s;", (date, courseid))
    times = cursor.fetchall()
    users_in_time = []
    for i in times:
        cursor = run_query(connection, "SELECT B.username, U.firstname, U.lastname FROM USERS U, BOOKEDTIMES B WHERE B.username = U.username AND B.timeid = %s;", (str(i[1]), ))
        users_in_time.append(cursor.fetchall())
    context = {'tee_times': times, 'users': users_in_time}
    return flask.jsonify(**context)

@views.route('/api/v1/course/date_transactions/<string:courseid>/<string:date>')
def get_date_transactions(courseid, date):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseid)
    cursor = run_query(connection, "SELECT L.timestamp, L.cost, L.user, T.teetime FROM Teetimes T, Ledger L WHERE CAST(L.timestamp AS DATE) = %s AND L.uniqid = %s AND L.timeid = T.timeid;", (date, courseid))
    transactions = cursor.fetchall()
    context = {'transactions': transactions}
    return flask.jsonify(**context)

@views.route('/api/v1/course_revenue/<string:courseid>/<string:date1>/<string:date2>')
def get_rev_weekly(courseid, date1, date2):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseid)
    cursor = run_query(connection, "SELECT COUNT(cost), SUM(cost), CAST(timestamp AS DATE) from ledger WHERE uniqid = %s" +
                        " AND CAST(timestamp as DATE) > %s AND CAST(timestamp AS DATE) < %s GROUP BY CAST(timestamp AS DATE);", (courseid, date1, date2))
    
    revenue = cursor.fetchall()
    revenue_by_day = [0, 0, 0, 0, 0, 0, 0]
    transactions_by_day = [0, 0, 0, 0, 0, 0, 0]
    for i in revenue:
        revenue_by_day[i[2].day - int(date1[-2:])] = i[1]
        transactions_by_day[i[2].day - int(date1[-2:])] = i[0]
    print(revenue_by_day)
    print(transactions_by_day)
    context = {'revenue_by_day': revenue_by_day, 'transactions_by_day': transactions_by_day}
    return flask.jsonify(**context)

def friends_in_time_helper(connection, good_user_times, userid):
    friends_in_time = []
    for i in good_user_times:
        print(i)
        cursor = run_query(connection, "SELECT U.firstname, U.lastname FROM USERS U, BOOKEDTIMES B WHERE B.timeid = %s AND B.username = U.username AND B.username in (SELECT U.username FROM USERS U, Friendships F WHERE ((F.userid2 = " +
                                        "%s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)));", (str(i[4]), userid, userid))
        user_friends = list(cursor.fetchall())
        friends_in_time.append(user_friends)
    return friends_in_time

def get_friends_times_helper(connection, userid):
    cursor = run_query(connection, "SELECT C.coursename, T.teetime, T.cost, T.spots, T.timeid FROM Teetimes T, Courses C WHERE C.uniqid = T.uniqid AND T.timeid" + 
                                   " IN (SELECT timeid FROM BOOKEDTIMES WHERE username IN (SELECT U.username FROM USERS U, Friendships F WHERE ((F.userid2 = " +
                                    "%s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)))) LIMIT 2;", (userid, userid))
    good_user_times = list(cursor.fetchall())
    friends_in_time = friends_in_time_helper(connection, good_user_times, userid)
    return good_user_times, friends_in_time

@views.route('/api/v1/friend_times/<string:userid>')
def get_friends_times(userid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    userid = user_helper(connection, userid)
    good_user_times, friends_in_time = get_friends_times_helper(connection, userid)
    context = {'good_user_times': good_user_times, 'user_friends': friends_in_time}
    return flask.jsonify(**context)

@views.route('/api/v1/search/friend_times/<string:userid>/<string:search>')
def get_friends_times_search(userid, search):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    userid = user_helper(connection, userid)
    search = search + '%'
    cursor = run_query(connection, "SELECT C.coursename, T.teetime, T.cost, T.spots, T.timeid FROM Teetimes T, Courses C WHERE C.uniqid = T.uniqid AND T.timeid" + " IN (SELECT timeid FROM BOOKEDTIMES WHERE username IN (SELECT U.username FROM USERS U, Friendships F WHERE (U.username like " + 
    "%s OR U.firstname like %s OR U.lastname like %s OR CONCAT(U.firstname, ' ', U.lastname) like %s) AND ((F.userid2 = %s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)))) LIMIT 2;", (search, search, search, search, userid, userid))
    good_user_times = cursor.fetchall()
    friends_in_time = []
    print({'good_user_times': good_user_times})
    print('hihihih')
    for i in good_user_times:
        cursor = run_query(connection, "SELECT U.firstname, U.lastname FROM USERS U, BOOKEDTIMES B WHERE B.timeid = %s AND B.username = U.username AND B.username in (SELECT U.username FROM USERS U, Friendships F WHERE ((F.userid2 = " +
                                        "%s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)));", (str(i[4]), userid, userid))
        user_friends = list(cursor.fetchall())
        print('hihihih')
        print(user_friends)
        friends_in_time.append(user_friends)
    context = {'good_user_times': good_user_times, 'user_friends': friends_in_time}
    return flask.jsonify(**context)


@views.route('/api/v1/remove_time_spot/<string:timeid>')
def start_transaction(timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT spots from Teetimes where timeid = %s;", (timeid, ))
    if (cursor.fetchone()[0] > 0):
        cursor = run_query(connection, "UPDATE Teetimes set spots = spots - 1 WHERE timeid = %s;", (timeid, ))
        context = {'error': 'none'}
    else:
        context = {'error': 'spot taken'}
    return flask.jsonify(**context)

@views.route('/api/v1/payment_error/<string:timeid>')
def transaction_error(timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "UPDATE Teetimes set spots = spots + 1 WHERE timeid = %s;", (timeid, ))
    context = {'error': 'none'}
    return flask.jsonify(**context)

@views.route('/api/v1/swipetimes/users/<string:timeid>')
def get_time_users(timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, """SELECT U.username, U.firstname, U.lastname, U.drinking, U.score, U.playstyle, U.descript, 
                                    U.college FROM USERS U, BOOKEDTIMES B WHERE B.timeid = %s AND U.username = B.username;""", (timeid, ))
    good_users = cursor.fetchall()
    context = {'good_users': good_users}
    return flask.jsonify(**context)

@views.route('/api/v1/course_info/<string:uniqid>')
def get_course_info(uniqid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT * FROM COURSES WHERE uniqid = %s;", (uniqid, ))
    course_info = cursor.fetchone()
    cursor = run_query(connection, "SELECT * FROM CourseReviews WHERE uniqid = %s ORDER BY TIMESTAMP DESC LIMIT 5", (uniqid, ))
    reviews = cursor.fetchall()
    cursor = run_query(connection, "SELECT ROUND(AVG(rating)) FROM CourseReviews WHERE uniqid = %s;", (uniqid, ))
    avg_rating = cursor.fetchone()[0]
    context = {'course_info': course_info, 'reviews': reviews, 'rating': avg_rating}
    print(course_info)
    return flask.jsonify(**context)


@views.route('/api/v1/courses/<string:courseid>/<string:date>')
def get_courses_times(courseid, date):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT * FROM COURSES WHERE uniqid = %s;", (courseid, ))
    course_info = cursor.fetchone()
    cursor = run_query(connection, "SELECT * FROM TEETIMES WHERE spots > 0 AND uniqid = %s" + 
    " AND CAST(teetime AS DATE) = %s;", (courseid, date))
    course_times = cursor.fetchall()
    context = {'course_info': course_info, 'course_times': course_times}
    return flask.jsonify(**context)

@views.route('/api/v1/courses/<string:courseid>')
def get_courses_info(courseid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseid)
    cursor = run_query(connection, "SELECT * FROM COURSES WHERE uniqid = %s;", (courseid, ))
    course_info = cursor.fetchone()
    context = {'course_info': course_info}
    return flask.jsonify(**context)

def get_my_friends_helper(connection, user, page):
    cursor = run_query(connection, "SELECT username, firstname, lastname FROM USERS U, Friendships F WHERE ((F.userid2 = %s AND U.Username = F.userid1) OR (F.userid1 = %s AND U.Username = F.userid2)) LIMIT 4 OFFSET %s;", (user, user, int(page)*3))
    my_friends = cursor.fetchall()
    has_more = False
    if (len(my_friends) == 4):
        has_more = True
    return my_friends, has_more

@views.route('/api/v1/my_friends/<string:user>/<string:page>')
def get_my_friends(user, page):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    my_friends, has_more = get_my_friends_helper(connection, user, page)
    context = {'results': my_friends, 'has_more': has_more}
    return flask.jsonify(**context)

# @views.route('/api/v1/login/check_attmpts/<string:user>')
# def check_attmpts(user):
#     connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     cursor = run_query(connection, "SELECT loginattmpts FROM USERS WHERE username = '" + user + "';")
#     too_many = False
#     if (cursor.fetchone() >= 5):
#         too_many = True
#     context = {'too_many': too_many}
#     return flask.jsonify(**context)


@views.route('/api/v1/admininfo/<string:user>')
def admin_info(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = admin_helper(connection, user)
    if (user == False):
        context = {'is_admin': False}
        return flask.jsonify(**context)
    cursor = run_query(connection, "SELECT SUM(cost) FROM ledger group by uniqid;")
    money = cursor.fetchone()[0]


@views.route('/api/v1/adminlogin/<string:username>/<string:password>')
def validate_admin(username, password):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT password, loginattmpts FROM USERS WHERE username = %s;", (username, ))
    data = cursor.fetchone()
    if (len(data) == 0):
        context = {'is_user': False, 'correct_login': False, 'too_many_attmpts': False}
        return flask.jsonify(**context)
    if (data[1] >= 5):
        context = {'is_user': True, 'correct_login': False, 'too_many_attmpts': True}
        return flask.jsonify(**context)
    is_user = False
    hashed_pass = data[0]
    if hashed_pass is not None:
        is_user = True
        pass_dict = {}
        pass_dict['split_pass'] = hashed_pass.split("$")
        pass_dict['salt'] = pass_dict['split_pass'][1]
        pass_dict['password'] = password
        pass_dict['algorithm'] = 'sha512'
        pass_dict['hash_obj'] = hashlib.new(pass_dict['algorithm'])
        pass_dict['pass_salt'] = (pass_dict['salt'] + pass_dict['password'])
        pass_dict['hash_obj'].update(pass_dict['pass_salt'].encode('utf-8'))
        pass_dict['pass_hash'] = pass_dict['hash_obj'].hexdigest()
        print(pass_dict['split_pass'][2] + "       ")
        print(pass_dict['pass_hash'])
        cookie = ''
        if pass_dict['split_pass'][2] != pass_dict['pass_hash']:
            cursor = run_query(connection, "UPDATE USERS set loginattmpts = loginattmpts + 1 WHERE username = %s;", (username, ))
            context = {'is_admin': False, 'correct_login': False, 'too_many_attmpts': False, 'cookie': cookie}
            return flask.jsonify(**context)
        else:
            cursor = run_query(connection, "UPDATE USERS set loginattmpts = 0 WHERE username = %s;", (username, ))
            cursor = run_query(connection, "SELECT COUNT(*) FROM ADMINS WHERE username = %s;", (username, ))
            is_admin = False
            if (cursor.fetchone()[0] == 1):
                is_admin = True
                cookie = make_cookie(username, '2')
            context = {'is_admin': is_admin, 'correct_login': True, 'too_many_attmpts': False, 'cookie': cookie}
            return flask.jsonify(**context)

@views.route('/api/v1/login/<string:username>/<string:password>')
def validate_user(username, password):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT password, loginattmpts FROM USERS WHERE username = %s;", (username, ))
    data = cursor.fetchone()
    if (len(data) == 0):
        context = {'is_user': False, 'correct_login': False, 'too_many_attmpts': False}
        return flask.jsonify(**context)
    if (data[1] >= 5):
        context = {'is_user': True, 'correct_login': False, 'too_many_attmpts': True}
        return flask.jsonify(**context)
    is_user = False
    is_admin = False
    correct_login = False
    cookie = ''
    hashed_pass = data[0]
    if hashed_pass is not None:
        is_user = True
        pass_dict = {}
        pass_dict['split_pass'] = hashed_pass.split("$")
        pass_dict['salt'] = pass_dict['split_pass'][1]
        pass_dict['password'] = password
        pass_dict['algorithm'] = 'sha512'
        pass_dict['hash_obj'] = hashlib.new(pass_dict['algorithm'])
        pass_dict['pass_salt'] = (pass_dict['salt'] + pass_dict['password'])
        pass_dict['hash_obj'].update(pass_dict['pass_salt'].encode('utf-8'))
        pass_dict['pass_hash'] = pass_dict['hash_obj'].hexdigest()
        print(pass_dict['split_pass'][2] + "       ")
        print(pass_dict['pass_hash'])
        cookie = ''
        if pass_dict['split_pass'][2] != pass_dict['pass_hash']:
            correct_login = False
            cursor = run_query(connection, "UPDATE USERS set loginattmpts = loginattmpts + 1 WHERE username = %s;", (username, ))
        else:
            correct_login = True
            cursor = run_query(connection, "UPDATE USERS set loginattmpts = 0 WHERE username = %s;", (username, ))
            cookie = make_cookie(username, '1')
    context = {'is_user': is_user, 'correct_login': correct_login, 'too_many_attmpts': False, 'cookie': cookie}
    return flask.jsonify(**context)


@views.route('/api/v1/create', methods =["POST"])
def create_user():
    # dbx.check_and_refresh_access_token()
    req = request.form
    if len(req['username']) < 6 or len(req['username']) > 15:
        context = {'error': 'Username must be between 6 and 15 characters'}
        return flask.jsonify(**context)
    if any(not c.isalnum() for c in req['username']):
        context = {'error': 'Username cannot have special characters (letters and numbers only)'}
        return flask.jsonify(**context)
    if not req['firstname'].isalpha():
        context = {'error': 'First name can only contain letters'}
        return flask.jsonify(**context)
    if not req['lastname'].isalpha():
        context = {'error': 'Last name can only contain letters'}
        return flask.jsonify(**context)
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM USERS WHERE username = %s;", (req['username'], ))
    if cursor.fetchone()[0] == 1:
        context = {'error': 'Username taken, please try another'}
        return flask.jsonify(**context)
    cursor = run_query(connection, "SELECT COUNT(*) FROM USERS WHERE email = %s;", (req['email'], ))
    if cursor.fetchone()[0] == 1:
        context = {'error': 'Email has already been linked to an account, please log in'}
        return flask.jsonify(**context)
    pass_dict = {}
    pass_dict['password'] = req['password']
    pass_dict['algorithm'] = 'sha512'
    pass_dict['salt'] = uuid.uuid4().hex
    pass_dict['hash_obj'] = hashlib.new(pass_dict['algorithm'])
    pass_dict['pass_salt'] = pass_dict['salt'] + pass_dict['password']
    pass_dict['hash_obj'].update(pass_dict['pass_salt'].encode('utf-8'))
    pass_dict['pass_hash'] = pass_dict['hash_obj'].hexdigest()
    pass_dict['password_db_string'] = "$".join([pass_dict['algorithm'],
                                                pass_dict['salt'],
                                                pass_dict['pass_hash']])
    image_url = ''
    print(req['hasphoto'])
    if (req['hasphoto'] == '1'):
        r = Image.open(request.files['file'])
        r_usuable = r.convert('RGB')
        img_arr = io.BytesIO()
        r_usuable.save(img_arr, format="JPEG")
        b64 = base64.b64encode(img_arr.getvalue())
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": imgbbkey,
            "image": b64,
        }
        res = requests.post(url, payload)
        res = res.json()
        print(res)
        image_url = res['data']['url']
        image_url = image_url.replace('\\', '')
    cursor = run_query(connection, """INSERT INTO USERS (username, password, firstname, lastname, 
    email, drinking, score, playstyle, descript, college, imageurl, active) VALUES (%s, """ +
    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '0');", (req['username'], pass_dict['password_db_string'], 
    req['firstname'], req['lastname'], req['email'], req['drinking'], req['score'], req['playstyle'], 
    req['descript'], req['college'], image_url))
    cookie = set_verification(req['username'])
    context = {'error': '', 'cookie': cookie}
    return flask.jsonify(**context)
    
@views.route('/api/v1/verify_email/<string:code>', methods =["PUT"])
def verify_email(code):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = translate_verification(connection, code)
    if (user == False):
        context = {'valid_link': False}
        return flask.jsonify(**context)
    cursor = run_query(connection, "DELETE FROM EMAILVERIF WHERE username = %s;", (user, ))
    cursor = run_query(connection, "UPDATE USERS set active = '1' WHERE username = %s;", (user, ))
    context = {'valid_link': True}
    return flask.jsonify(**context)
    

@views.route('/api/v1/register_course', methods =["POST"])
def register_course():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM COURSES WHERE coursename = %s AND town = %s AND state = %s;", (req['name'], req['town'], req['state']))
    count = cursor.fetchone()[0]
    if count == 1:
        context = {'error': 'Course has already been registered'}
        return flask.jsonify(**context)
    cursor = run_query(connection, "SELECT COUNT(*) FROM PENDINGCOURSES WHERE coursename = %s AND town = %s AND state = %s;", (req['name'], req['town'], req['state']))
    count = cursor.fetchone()[0]
    if count == 1:
        context = {'error': 'Course has already been submitted as is waiting approval. We will contact you shortly and thank you for your patience'}
        return flask.jsonify(**context)
    course_list, lat, lon = location_search_helper(req['zip'], 25)
    pass_dict = {}
    pass_dict['password'] = req['password']
    pass_dict['algorithm'] = 'sha512'
    pass_dict['salt'] = uuid.uuid4().hex
    pass_dict['hash_obj'] = hashlib.new(pass_dict['algorithm'])
    pass_dict['pass_salt'] = pass_dict['salt'] + pass_dict['password']
    pass_dict['hash_obj'].update(pass_dict['pass_salt'].encode('utf-8'))
    pass_dict['pass_hash'] = pass_dict['hash_obj'].hexdigest()
    pass_dict['password_db_string'] = "$".join([pass_dict['algorithm'],
                                                pass_dict['salt'],
                                                pass_dict['pass_hash']])
    image_url = ''
    print(req['hasphoto'])
    if (req['hasphoto'] == '1'):
        r = Image.open(request.files['file'])
        r_usuable = r.convert('RGB')
        img_arr = io.BytesIO()
        r_usuable.save(img_arr, format="JPEG")
        b64 = base64.b64encode(img_arr.getvalue())
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": imgbbkey,
            "image": b64,
        }
        res = requests.post(url, payload)
        res = res.json()
        print(res)
        image_url = res['data']['url']
        image_url = image_url.replace('\\', '')
    cursor = run_query(connection, """INSERT INTO PENDINGCOURSES (coursename, latitude, longitude, street, town, state, 
    zip, adminemail, adminpassword, adminphone, canedit, imageurl) VALUES (%s, """ +
    "%s, %s, %s, %s, %s, %s, %s, %s, %s, '0');", (req['name'], str(lat), str(lon), req['address'], req['town'], 
    req['state'], req['zip'], req['email'], pass_dict['password_db_string'], req['phone'], image_url))
    context = {'error': ''}
    return flask.jsonify(**context)

def calculate_order_amount(timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT cost FROM TEETIMES WHERE timeid = %s;", (timeid, ))
    cost = float(cursor.fetchone()[0])
    return cost

stripe.api_key = 'sk_test_51LIIQAG2PmM18WKObcR2HE4AzVIwEZ1vwp75XdDi6IawslHyWzVtJXLmKILzRLYFEr8xY3yXXJRGJSWcIdduPJ5n001apPDssN'

@views.route('/create-payment-intent', methods=['POST'])
def create_payment():
    data = json.loads(flask.request.data)
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT C.coursename, C.street, C.state, C.zip, T.teetime FROM COURSES C, TEETIMES T WHERE T.timeid = %s" +
                       " AND T.uniqid = C.uniqid;", (data['timeid'], ))
    # Create a PaymentIntent with the order amount and currency
    course_info = cursor.fetchone()
    cost = calculate_order_amount(data['timeid'])
    print(round((cost + (cost*.0816)), 2))
    intent = stripe.PaymentIntent.create(
        amount= int(round((cost + (cost*.0816)), 2) * 100),
        currency='usd',
        payment_method_types=["card"],
    )
    return flask.jsonify({
        'clientSecret': intent['client_secret'],
        'cost': cost,
        'course_info': course_info
    })

@views.route('/api/v1/users/<string:username>')
def get_single_user(username):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    username = user_helper(connection, username)
    cursor = run_query(connection, "SELECT username, password, firstname, lastname, email, drinking, score, college, playstyle, descript, imageurl FROM USERS WHERE username = %s;", (username, ))
    return flask.jsonify({'user': cursor.fetchone()})

@views.route('/api', methods = ["PUT"])
def inc():
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT * FROM USERS;")
    j = 1
    for i in cursor.fetchall():
        cursor = run_query(connection, "UPDATE USERS SET userid = %s WHERE username = %s;", (str(j), i[0]))
        j = j + 1

@views.route('/api/v1/edit', methods=["PUT"])
def edit_user():
    req = request.form
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, req['oldusername'])
    print(req['username'])
    if len(req['username']) < 6 or len(req['username']) > 15:
        context = {'error': 'Username must be between 6 and 15 characters'}
        return flask.jsonify(**context)
    if any(not c.isalnum() for c in req['username']):
        context = {'error': 'Username cannot have special characters (letters and numbers only)'}
        return flask.jsonify(**context)
    if not req['firstname'].isalpha():
        context = {'error': 'First name can only contain letters'}
        return flask.jsonify(**context)
    if not req['lastname'].isalpha():
        context = {'error': 'Last name can only contain letters'}
        return flask.jsonify(**context)
    if (request.files['file'] is not None):
        r = Image.open(request.files['file'])
        r_usuable = r.convert('RGB')
        img_arr = io.BytesIO()
        r_usuable.save(img_arr, format="JPEG")
        b64 = base64.b64encode(img_arr.getvalue())
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": imgbbkey,
            "image": b64,
        }
        res = requests.post(url, payload)
        res = res.json()
        image_url = res['data']['url']
        image_url = image_url.replace('\\', '')
        print(image_url)
    cursor = run_query(connection, "UPDATE USERS SET username = %s, firstname = %s, " + 
    "lastname = %s, email = %s, drinking = %s, score = %s, playstyle = %s, descript = %s, " + 
    "college = %s, imageurl = %s WHERE username = %s;", (req['username'], req['firstname'], req['lastname'],
    req['email'], req['drinking'], req['score'], req['playstyle'], req['descript'], req['college'], image_url, user)) 
    user = cursor.fetchone()
    context = {'error': '', 'user': user}
    return flask.jsonify(**context)

@views.route('/api/v1/course_schedule/<string:courseuser>/<string:day>')
def course_profile_data(courseuser, day):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseuser)
    cursor = run_query(connection, "SELECT * FROM COURSES WHERE uniqid = %s;", (courseid, ))
    course_info = cursor.fetchone()
    cursor = run_query(connection, "SELECT days, time, cost FROM TEETIMESCHEDULE WHERE course_id = %s AND days = %s ORDER BY time;", (courseid, day))
    tee_time_sched = list(cursor.fetchall())
    context = {"course_info": course_info, "tee_sched": tee_time_sched}
    return json.dumps(context, default=str)

@views.route('/api/v1/course_schedule/add/<string:courseid>', methods=["POST"])
def course_add_sched(courseuser):
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseuser)
    for i in req['days']:
        cursor = run_query(connection, "INSERT INTO TEETIMESCHEDULE (course_id, days, time, cost) VALUES (%s, %s, " +
                        "%s, %s);", (courseid, i, req["time"], req["cost"]))
    message = cursor.fetchone()
    context = {"message": message}
    return flask.jsonify(**context)

@views.route('/api/v1/course_schedule/check_day/<string:courseid>/<string:time>')
def course_check_days(courseuser, time):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseuser)
    cursor = run_query(connection, "SELECT days FROM TEETIMESCHEDULE WHERE course_id = %s AND time = %s;", (courseid, time))
    checked_days = cursor.fetchall()
    is_checked = [False, False, False, False, False, False, False]
    for i in checked_days:
        is_checked[i] = True
    context = {"checked_days": is_checked}
    return flask.jsonify(**context)

@views.route('/api/v1/course_schedule/holidays/<string:courseuser>/<string:page>')
def course_closed_dates(courseuser, page):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, courseuser)
    cursor = run_query(connection, "SELECT * FROM COURSECLOSEDDATES WHERE uniqid = %s and date > CURRENT_TIMESTAMP ORDER BY date LIMIT 6 OFFSET %s;", (courseid, int(page)*5))
    closures = cursor.fetchall()
    context = {'closures': closures}
    return flask.jsonify(**context)

@views.route('/api/v1/course_schedule/holidays/add', methods=["POST"])
def course_add_closure():
    req = flask.request.json
    print(req)
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    courseid = user_helper(connection, req['user'])
    cursor = run_query(connection, "INSERT INTO COURSECLOSEDDATES (date, uniqid) VALUES (%s, %s);", (req['date'], courseid))
    context = {'error': ''}
    return flask.jsonify(**context)

@views.route('/api/v1/course_login/<string:email>/<string:password>')
def validate_course_admin(email, password):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT password, uniqid FROM USERS WHERE adminemail = %s;", (email, ))
    data = cursor.fetchone()
    if (len(data) == 0):
        context = {'is_user': False, 'correct_login': False, 'too_many_attmpts': False}
        return flask.jsonify(**context)
    is_user = False
    correct_login = False
    cookie = ''
    hashed_pass = data[0]
    if hashed_pass is not None:
        is_user = True
        pass_dict = {}
        pass_dict['split_pass'] = hashed_pass.split("$")
        pass_dict['salt'] = pass_dict['split_pass'][1]
        pass_dict['password'] = password
        pass_dict['algorithm'] = 'sha512'
        pass_dict['hash_obj'] = hashlib.new(pass_dict['algorithm'])
        pass_dict['pass_salt'] = (pass_dict['salt'] + pass_dict['password'])
        pass_dict['hash_obj'].update(pass_dict['pass_salt'].encode('utf-8'))
        pass_dict['pass_hash'] = pass_dict['hash_obj'].hexdigest()
        print(pass_dict['split_pass'][2] + "       ")
        print(pass_dict['pass_hash'])
        if pass_dict['split_pass'][2] != pass_dict['pass_hash']:
            correct_login = False
        else:
            correct_login = True
            cookie = make_cookie(data[1], '0')
    context = {'is_user': is_user, 'correct_login': correct_login, 'too_many_attmpts': False, 'cookie': cookie}
    return flask.jsonify(**context)

@views.route('/api/v1/users/add_friend', methods=["POST"])
def create_friend_req():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    poster = user_helper(connection, req['poster'])
    cursor = run_query(connection, "INSERT INTO REQUESTEDFRIENDS (username1, username2) VALUES (%s, %s);", (poster, req['receiver']))
    cursor = run_query(connection, "UPDATE USERS SET notifications = notifications + 1 WHERE username = %s;", (req['receiver'], ))
    message = "completed"
    context = {'message': message}
    return flask.jsonify(**context)

@views.route('/api/v1/add_receipt', methods=["POST"])
def add_receipt():
    req = flask.request.json
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "INSERT INTO Ledger (user, timeid, uniqid, cost) VALUES (%s, %s, %s, %s);", (req['user'], req['time'], req['course'], req['cost']))
    return flask.jsonify("")

@views.route('/api/v1/accept_request/<string:accepting_user>/<string:accepted_user>', methods=["POST"])
def accept_friend_req(accepting_user, accepted_user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    accepting_user = user_helper(connection, accepting_user)
    users = sorted([accepting_user, accepted_user])
    cursor = run_query(connection, "INSERT INTO FRIENDSHIPS (userid1, userid2) VALUES (%s, %s);", (users[0], users[1]))
    cursor = run_query(connection, "DELETE FROM REQUESTEDFRIENDS WHERE username1 = %s AND username2 = %s;", (accepted_user, accepting_user))
    message = "completed"
    context = {'message': message}
    return flask.jsonify(**context)

@views.route('/api/v1/deny_request/<string:accepting_user>/<string:accepted_user>', methods=["DELETE"])
def deny_friend_req(accepting_user, accepted_user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "DELETE FROM REQUESTEDFRIENDS WHERE username1 = %s AND username2 = %s;", (accepted_user, accepting_user))
    message = "completed"
    context = {'message': message}
    return flask.jsonify(**context)

def getThreeWeeks():
    today = str(datetime.date.today())
    split = today.split('-')
    year = int(split[0])
    month = int(split[1])
    day = int(split[2])
    print(str(year) + " " + str(month) + " " + str(day))
    if month == 4 or month == 6 or month == 9 or month == 11:
        if day + 21 > 30:
            month = month + 1
        day = (day + 21) % 30
    elif month == 2:
        if day + 21 > 28:
            month = month + 1
        day = (day + 21) % 28
    elif month == 12:
        if day + 21 > 31:
            month = 1
            year = year + 1
        day = (day + 21) % 31
    else:
        if day + 21 > 31:
            month = month + 1
        day = (day + 21) % 31
    return str(year) + '-' + str(month) + '-' + str(day)

@views.route('/api/v1/messages/<string:user1>/<string:user2>/<string:page>/<string:offset>')
def get_messages(user1, user2, page, offset):
    print(offset)
    x = 20*int(page) + int(offset)
    off = x
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user1 = user_helper(connection, user1)
    cursor = run_query(connection, "SELECT * FROM Messages WHERE (userid1 = %s AND userid2 = " + 
                       "%s) OR (userid2 = %s AND userid1 = %s) ORDER BY timestamp DESC LIMIT 21 OFFSET %s;", (user1, user2, user1, user2, off))
    messages = cursor.fetchall()
    print(len(messages))
    last = False
    print(len(messages) < 21)
    if len(messages) < 21:
        last = True
    messages = messages[0:20]
    context = {'messages': messages, 'last': last, 'logged_user': user1}
    return flask.jsonify(**context)

@views.route('/api/v1/message_previews/<string:user>')
def get_message_previews(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT max(messageid) FROM Messages WHERE userid1 = %s OR userid2 = %s GROUP BY userid1, userid2;", (user, user))
    interim = [item[0] for item in cursor.fetchall()]
    print(interim)
    interim.sort(reverse=True)
    last_messages = []
    for i in interim:
        cursor = run_query(connection, "SELECT userid1, userid2, content, timestamp FROM Messages WHERE messageid = %s;", (str(i), ))
        last_message = cursor.fetchall()
        last_messages.append(last_message)
    last_messages_filtered = []
    matching_users = []
    for i in last_messages:
        if i[0][0] == user:
            if i[0][1] not in matching_users:
                last_messages_filtered.append([i[0][3], i[0][2]])
                matching_users.append(i[0][1])
        else:
            if i[0][0] not in matching_users:
                last_messages_filtered.append([i[0][3], i[0][2]])
                matching_users.append(i[0][0])
    context = {'last_messages': last_messages_filtered, 'matching_users': matching_users}
    return flask.jsonify(**context)

            

    context = {'messages': messages, 'last': last}
    return flask.jsonify(**context)

@views.route('/api/v1/posts/<string:user>')
def get_posts(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT * FROM Posts WHERE username = %s ORDER BY timestamp DESC LIMIT 3;", (user, ))
    posts = cursor.fetchall()
    more = True
    if (len(posts) != 3):
        more = False
    context = {'has_more': more, 'posts': posts, 'user': user}
    return flask.jsonify(**context)

@views.route('/api/v1/message_count/<string:user1>/<string:user2>')
def get_message_count(user1, user2):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT COUNT(*) FROM Messages WHERE (userid1 = %s AND userid2 = %s) OR (userid2 = %s AND userid1 = %s);", (user1, user2, user1, user2))
    count = cursor.fetchone()[0]
    context = {'count': count}
    return flask.jsonify(**context)

@views.route('/api/v1/admins/')
def get_admins():
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT username FROM ADMINS")
    admins = cursor.fetchall()
    context = {'admins': admins}
    return flask.jsonify(**context)

@views.route('/api/v1/my_prof/<string:user>')
def get_my_times(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT C.coursename, T.teetime, T.cost, T.spots, T.timeid FROM Courses C, Teetimes T, BookedTimes B WHERE B.username = %s AND B.timeid = T.timeid AND C.uniqid = T.uniqid AND T.teetime > CURRENT_TIMESTAMP;", (user, ))
    my_times = cursor.fetchall()
    cursor = run_query(connection, "SELECT * FROM Posts P WHERE P.username = %s ORDER BY timestamp DESC LIMIT 4;", (user, ))
    my_posts = cursor.fetchall()
    has_more_posts = False
    if (len(my_posts) == 4):
        has_more_posts: True
    my_friends, has_more_friends = get_my_friends_helper(connection, user, '0')
    context = {'my_times': my_times, 'my_posts': my_posts, 'has_more_posts': has_more_posts, 'my_friends': my_friends, 'has_more_friends': has_more_friends}
    return flask.jsonify(**context)

@views.route('/api/v1/my_posts/<string:user>')
def get_my_posts(user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT * FROM Posts P WHERE P.username = %s ORDER BY timestamp DESC LIMIT 4;", (user, ))
    my_posts = cursor.fetchall()
    has_more_posts = False
    if (len(my_posts) == 4):
        has_more_posts: True
    context = {'my_posts': my_posts, 'has_more_posts': has_more_posts}
    return flask.jsonify(**context)

@views.route('/api/v1/teetime/<string:timeid>/<string:user>')
def get_time_info(timeid, user):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    user = user_helper(connection, user)
    cursor = run_query(connection, "SELECT C.coursename, T.teetime, T.cost, T.spots, T.cart, C.street, C.town, C.state, C.zip, C.uniqid, C.imageurl FROM Courses C, Teetimes T WHERE T.timeid = " +
                                    "%s AND C.uniqid = T.uniqid;", (timeid, ))
    time_info = list(cursor.fetchone())
    cursor = run_query(connection, "SELECT U.username, U.firstname, U.lastname, U.email, U.drinking, U.score, U.playstyle, U.descript, U.college, U.imageurl FROM Users U, BookedTimes B WHERE U.username = B.username AND B.timeid = %s;", (timeid, ))
    print(time_info)
    time_users = cursor.fetchall()
    in_time = False
    for i in time_users:
        if i[0] == user:
            in_time = True
    time_info.append(time_users)
    context = {"time_info": time_info, 'in_time': in_time}
    return flask.jsonify(**context)

@views.route('/api/v1/payment_confirmed/<string:timeid>', methods = ["PUT"])
def change_spots(timeid):
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, "SELECT spots FROM teetimes WHERE timeid = %s;", (timeid, ))
    if (cursor.fetchone() != 0):
        cursor = run_query(connection, "UPDATE teetimes SET spots = spots - 1 WHERE timeid = %s;", (timeid, ))
        context = {'message': ''}
    else:
        context = {'message': 'error'}
    return flask.jsonify(**context)



# @scheduler.scheduled_job(IntervalTrigger(hours=24), methods=["POST"])
# def update_times():
#     connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
#     cursor = run_query(connection, "SELECT * FROM COURSES;")
#     courses = cursor.fetchall()
#     days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#     three_weeks = getThreeWeeks()
#     for i in courses:
#         cursor = run_query(connection, "SELECT * FROM TEETIMESCHEDULE WHERE course_id = '" + i[0] + "' AND days like '%" + days_of_the_week[datetime.today().weekday()] + "%';")
#         sched = cursor.fetchall()
#         for j in sched:
#             cursor = run_query(connection, "INSERT INTO TEETIMES (uniqid, teetime, cost, spots) VALUES ('" + i[0] + "', '" + three_weeks + " " + i[2] + "', '" + i[3] + "', 4);")
#     context = {'message': 'completed nightly batch'}
#     return flask.jsonify("**context")
