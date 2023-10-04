#!/usr/bin/python3
import sqlite3
import json
from bottle import *

db = sqlite3.connect("shit.db")
cursor = db.cursor()

statusStr={
    'success':'{"status": "SUC"}',
    'no_user':'{"status": "NO_USER"}',
    'uid_exist':'{"status": "UID_EXIST"}',
    'name_exist':'{"status": "NAME_EXIST"}',
    'no_record':'{"status": "NO_RECORD"}'
}

def findUsernameByUid(uid):
    cursor.execute("select name from users where uid=%s", (uid))
    username = cursor.fetchone()[0]
    if not username:
        return False

    return username


@route("/get_username")
def getUsername():
    uid = int(request.query["uid"])
    username = findUsernameByUid(uid)
    if not username:
        return statusStr['no_user']

    return '{"status": "SUC", "username": %s}' % username


@route("/sign_in", method="POST")
def signIn():
    args = request.forms
    uid = args.get("uid")
    if not findUsernameByUid(uid):
        return statusStr['no_user']
    
    cursor.execute(
        'insert into records(uid, sign_dt) values(%s, datetime("now"))', (uid)
    )

    db.commit()
    return statusStr['success']


@route("/modify_info", method="POST")
def modifyInfo():
    args = json.loads(request.body)
    if args["to-change-uid"]:
        currentUid=args["uid"]
        newUid = args["new-uid"]
        
        cursor.execute('select uid from users where uid=%s', (currentUid))
        if not cursor.fetchone():
            return statusStr['no_user']

        cursor.execute('select uid from users where uid=%s', (newUid))
        if cursor.fetchone():
            return statusStr['uid_exist']
        
        cursor.execute('update users set uid=%s where uid=%s', (newUid, currentUid))
        cursor.execute('update records set uid=%s where uid=%s', (newUid, currentUid))
        db.commit()
        return statusStr['success']

    if args["to-change-name"]:
        uid = args["uid"]
        newName = args["new-name"]

        cursor.execute('select uid from users where uid=%s', (uid))
        if not cursor.fetchone():
            return statusStr['no_user']
        
        cursor.execute('select uid from users where name=%s', (newName))
        if cursor.fetchone():
            return statusStr['name_exist']

        cursor.execute('update users set name=%s where uid=%s', (newName, uid))
        db.commit()
        return statusStr['success']
    
    return '{"status": "WTF"}'

@route("/list_records")
def getRecords():
    cursor.execute('select * from records')
    records = cursor.fetchall()
    if not records:
        return statusStr['no_record']
    
    return '{"status": "SUC", "records": %s}' % records

@route("/add_user",method='POST')
def addUser():
    args = request.forms
    uid = args["uid"]
    name = args["name"]

    cursor.execute('select uid from users where uid=%s', (uid))
    if cursor.fetchone():
        return statusStr['uid_exist']
    
    cursor.execute('select uid from users where name=%s', (name))
    if cursor.fetchone():
        return statusStr['name_exist']

    cursor.execute('insert into users(uid, name) values(%s, %s)', (uid, name))
    db.commit()
    return statusStr['success']

@route("/del_user", method='POST')
def delUser():
    args = request.forms
    uid = args["uid"]

    cursor.execute('select uid from users where uid=%s', (uid))
    if not cursor.fetchone():
        return statusStr['no_user']

    cursor.execute('delete from users where uid=%s', (uid))
    cursor.execute('delete from records where uid=%s', (uid))
    db.commit()
    return statusStr['success']

@route("/list_users")
def listUsers():
    cursor.execute('select uid, name from users')
    users = cursor.fetchall()
    if not users:
        return statusStr['no_record']
    
    return '{"status": "SUC", "users": %s}' % users


try:
    run(host="0.0.0.0", port=2333)

finally:
    db.close()
    exit()
