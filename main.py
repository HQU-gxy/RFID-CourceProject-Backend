#!/usr/bin/python3
import sqlite3
from os import path
from bottle import *

if not path.exists("shit.db"):
    db = sqlite3.connect("shit.db")
    cursor = db.cursor()
    cursor.execute("create table users(uid text, name text)")
    cursor.execute("create table records(uid text, sign_dt text)")
    db.commit()
    db.close()
    print("DB file not found, created one")

db = sqlite3.connect("shit.db")
cursor = db.cursor()

statusStr = {
    "success": '{"status": "SUC"}',
    "no_user": '{"status": "NO_USER"}',
    "uid_exist": '{"status": "UID_EXIST"}',
    "name_exist": '{"status": "NAME_EXIST"}',
    "no_record": '{"status": "NO_RECORD"}',
}


def findUsernameByUid(uid: str):
    cursor.execute('select name from users where uid="%s"' % uid)
    username = cursor.fetchone()
    if not username:
        return False

    return username[0]


@route("/get_username")
def getUsername():
    uid = request.query["uid"]
    username = findUsernameByUid(uid)
    if not username:
        return statusStr["no_user"]

    return '{"status": "SUC", "username": "%s"}' % username


@route("/sign_in")
def signIn():
    uid = request.query["uid"]
    if not findUsernameByUid(uid):
        return statusStr["no_user"]

    cursor.execute(
        'insert into records(uid, sign_dt) values("%s", datetime("now"))' % uid
    )

    db.commit()
    return statusStr["success"]


@route("/modify_info", method="POST")
def modifyInfo():
    args = request.forms
    if args["to-change-uid"] == "1":
        currentUid = args["uid"]
        newUid = args["new-uid"]

        cursor.execute('select uid from users where uid="%s"' % currentUid)
        if not cursor.fetchone():
            return statusStr["no_user"]

        cursor.execute('select uid from users where uid="%s"' % newUid)
        if cursor.fetchone():
            return statusStr["uid_exist"]

        cursor.execute(
            'update users set uid="%s" where uid="%s"' % (newUid, currentUid)
        )
        cursor.execute(
            'update records set uid="%s" where uid="%s"' % (newUid, currentUid)
        )
        db.commit()
        return statusStr["success"]

    if args["to-change-name"] == "1":
        uid = args["uid"]
        newName = args["new-name"]

        cursor.execute('select uid from users where uid="%s"' % uid)
        if not cursor.fetchone():
            return statusStr["no_user"]

        cursor.execute('select uid from users where name="%s"' % newName)
        if cursor.fetchone():
            return statusStr["name_exist"]

        cursor.execute('update users set name="%s" where uid="%s"' % (newName, uid))
        db.commit()
        return statusStr["success"]

    return '{"status": "WTF"}'


@route("/list_records")
def getRecords():
    cursor.execute("select * from records")
    records = cursor.fetchall()
    if not records:
        return statusStr["no_record"]

    recordList = []
    for rec in records:
        recordList.append({"username": findUsernameByUid(rec[0]), "sign_dt": rec[1]})

    return '{"status": "SUC", "records": %s}' % recordList


@route("/add_user", method="POST")
def addUser():
    args = request.forms
    uid = args["uid"]
    name = args["name"]

    cursor.execute('select uid from users where uid="%s"' % uid)
    if cursor.fetchone():
        return statusStr["uid_exist"]

    cursor.execute('select uid from users where name="%s"' % name)
    if cursor.fetchone():
        return statusStr["name_exist"]

    cursor.execute('insert into users(uid, name) values("%s", "%s")' % (uid, name))
    db.commit()
    return statusStr["success"]


@route("/del_user", method="POST")
def delUser():
    args = request.forms
    uid = args["uid"]

    cursor.execute('select uid from users where uid="%s"' % uid)
    if not cursor.fetchone():
        return statusStr["no_user"]

    cursor.execute('delete from users where uid="%s"' % uid)
    cursor.execute('delete from records where uid="%s"' % uid)
    db.commit()
    return statusStr["success"]


@route("/list_users")
def listUsers():
    cursor.execute("select uid, name from users")
    users = cursor.fetchall()
    if not users:
        return statusStr["no_record"]

    userList = []
    for user in users:
        userList.append({"uid": user[0], "name": user[1]})

    return '{"status": "SUC", "users": %s}' % userList


try:
    run(host="0.0.0.0", port=2333)

finally:
    db.close()
    exit()
