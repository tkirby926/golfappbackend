from golfappbackend.views import create_server_connection, run_query

def create_tables():
    connection = create_server_connection('localhost', 'root', 'playbutton68', 'golfbuddies_data')
    cursor = run_query(connection, """CREATE TABLE `teetimes` (
        `timeid` int NOT NULL AUTO_INCREMENT,
        `teetime` datetime DEFAULT NULL,
        `uniqid` varchar(20) DEFAULT NULL,
        `cost` varchar(20) DEFAULT NULL,
        `spots` int DEFAULT NULL,
        `cart` bit(1) DEFAULT NULL,
        PRIMARY KEY (`timeid`),
        KEY `uniqid` (`uniqid`)
        )""")
    cursor = run_query(connection, """CREATE TABLE `users` (
        `username` varchar(20) NOT NULL,
        `firstname` varchar(30) DEFAULT NULL,
        `lastname` varchar(30) DEFAULT NULL,
        `email` varchar(40) DEFAULT NULL,
        `password` varchar(180) DEFAULT NULL,
        `created` datetime DEFAULT CURRENT_TIMESTAMP,
        `drinking` varchar(40) DEFAULT NULL,
        `score` varchar(40) DEFAULT NULL,
        `playstyle` varchar(40) DEFAULT NULL,
        `descript` text,
        `college` varchar(40) DEFAULT NULL,
        `notifications` int DEFAULT NULL,
        `loginattmpts` int DEFAULT NULL,
        `imageurl` varchar(60) DEFAULT NULL,
        `active` char(1) DEFAULT NULL,
        PRIMARY KEY (`username`)
        )""")

    cursor = run_query(connection, """CREATE TABLE `admins` (
        `username` varchar(20) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `bookedtimes` (
        `username` varchar(20) DEFAULT NULL,
        `timeid` varchar(20) DEFAULT NULL,
        KEY `username` (`username`),
        KEY `timeid` (`timeid`),
        CONSTRAINT `bookedtimes_ibfk_1` FOREIGN KEY (`username`) REFERENCES `USERS` (`username`)
        )""")
    cursor = run_query(connection, """CREATE TABLE `cookies` (
        `username` varchar(20) DEFAULT NULL,
        `sessionid` varchar(32) DEFAULT NULL,
        `user` char(1) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `coursecloseddates` (
        `date` date DEFAULT NULL,
        `uniqid` int DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `coursereviews` (
        `uniqid` int DEFAULT NULL,
        `rating` int DEFAULT NULL,
        `description` varchar(300) DEFAULT NULL,
        `timestamp` datetime DEFAULT NULL,
        `username` varchar(20) DEFAULT NULL
        )""") 

    cursor = run_query(connection, """CREATE TABLE `courses` (
        `uniqid` int NOT NULL AUTO_INCREMENT,
        `latitude` varchar(20) DEFAULT NULL,
        `longitude` varchar(20) DEFAULT NULL,
        `coursename` varchar(80) DEFAULT NULL,
        `street` varchar(40) DEFAULT NULL,
        `town` varchar(40) DEFAULT NULL,
        `zip` varchar(20) DEFAULT NULL,
        `state` varchar(30) DEFAULT NULL,
        `adminemail` varchar(40) DEFAULT NULL,
        `adminpassword` varchar(20) DEFAULT NULL,
        `adminphone` varchar(10) DEFAULT NULL,
        `imageurl` varchar(60) DEFAULT NULL,
        `canedit` char(1) DEFAULT NULL,
        `auth` char(1) DEFAULT NULL,
        PRIMARY KEY (`uniqid`)
        )""")  
    cursor = run_query(connection, """CREATE TABLE `emailverif` (
        `username` varchar(20) DEFAULT NULL,
        `emailcode` varchar(16) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `friendships` (
        `UserId1` varchar(20) DEFAULT NULL,
        `UserId2` varchar(20) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `ledger` (
        `timeid` varchar(20) DEFAULT NULL,
        `uniqid` varchar(20) DEFAULT NULL,
        `Cost` varchar(20) DEFAULT NULL,
        `user` varchar(20) DEFAULT NULL,
        `timestamp` datetime DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `messages` (
        `content` varchar(700) DEFAULT NULL,
        `userid1` varchar(20) DEFAULT NULL,
        `userid2` varchar(20) DEFAULT NULL,
        `timestamp` datetime DEFAULT NULL,
        `messageid` int NOT NULL AUTO_INCREMENT,
        PRIMARY KEY (`messageid`)
        )""")
    cursor = run_query(connection, """CREATE TABLE `posts` (
        `content` varchar(700) DEFAULT NULL,
        `username` varchar(20) DEFAULT NULL,
        `timestamp` datetime DEFAULT NULL,
        `link` varchar(20) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `requestedfriends` (
        `username1` varchar(20) DEFAULT NULL,
        `username2` varchar(20) DEFAULT NULL
        )""")
    cursor = run_query(connection, """CREATE TABLE `reviews` (
        `username` varchar(20) DEFAULT NULL,
        `content` varchar(400) DEFAULT NULL,
        `timestamp` datetime DEFAULT NULL,
        `rating` int DEFAULT NULL
        )""")
    cursor = run_query(connection, """ CREATE TABLE `teetimeschedule` (
        `course_id` int DEFAULT NULL,
        `days` text,
        `time` time DEFAULT NULL,
        `cost` varchar(10) DEFAULT NULL
        )""")

    

    
    