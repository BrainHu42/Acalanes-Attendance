import json
import psycopg2.errors
from datetime import datetime, timezone
import pip._vendor.requests as requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, request, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from AAT.db import get_db
from AAT.account import getPeriod

bp = Blueprint('zoomAPI', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        if request.headers['authorization'] == 'RmRNbnqWSJym7KoMXK1uzQ':
            #assert request is from zoom
            event = request.json
            payload = event['payload']
            db_conn = get_db()
            db = db_conn.cursor()
            #make sure no SQL is executed before rowcount check
            if event['event'] == 'meeting.participant_admitted':
                admitted = payload['object']
                student = admitted['participant']
                uuid = admitted['uuid']
                joinTime = student['date_time']

                userID = ''
                if 'id' in student:
                    userID = student['id']
                    db.execute('UPDATE student SET currentMeeting = %s, joinTime = %s WHERE userID = %s AND confidence > 2 AND currentMeeting <> %s;', (uuid, joinTime, userID, uuid))
                #try to indentify student using zoom userID
                if db.rowcount <= 0:
                    #if that doesn't work, try with username
                    name = ''
                    if 'user_name' in student:
                        name = student['user_name']
                        if userID == '' or userID == None:
                            db.execute('UPDATE student SET currentMeeting = %s, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, joinTime, name, uuid))    
                        else:
                            #we know the userID is corret for sure
                            db.execute('UPDATE student SET currentMeeting = %s, userID = %s, confidence = 3, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, userID, joinTime, name, uuid))
                        
                        if db.rowcount <= 0:
                            #try different format
                            words = name.split(',')
                            if len(words) >= 2:
                                name = words[1].strip()+" "+words[0]
                                if userID == '' or userID == None:
                                    db.execute('UPDATE student SET currentMeeting = %s, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, joinTime, name, uuid))    
                                else:
                                    #we know the userID is corret for sure
                                    db.execute('UPDATE student SET currentMeeting = %s, userID = %s, confidence = 3, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, userID, joinTime, name, uuid))
                    else:
                        #can't do anything without name
                        return Response(status=200, mimetype='application/json')

                    #if that doesn't work, STRANGER DANGER
                    if db.rowcount <= 0:
                        db.execute('SELECT * FROM student WHERE name = %s OR (userID = %s AND (confidence > 2 OR currentMeeting = %s));', (name, userID, uuid))
                        if db.rowcount <= 0:
                            db.execute('UPDATE stranger SET currentMeeting = %s, joinTime = %s, name = %s WHERE userID = %s AND currentMeeting <> %s;', (uuid, joinTime, name, userID, uuid))
                            if db.rowcount <= 0:
                                try:
                                    db.execute('INSERT INTO stranger (userID, currentMeeting, joinTime, name) VALUES (%s, %s, %s, %s);', (userID, uuid, joinTime, name))
                                except psycopg2.errors.UniqueViolation:
                                    return Response(status=200, mimetype='application/json')

                db_conn.commit()

            # elif event['event'] == 'meeting.participant_joined':
            #     joined = payload['object']
            #     student = joined['participant']
            #     uuid = joined['uuid']
            #     joinTime = student['join_time']
            #     #skip if teacher
            #     if joined['host_id'] == student['id']:
            #         return Response(status=200, mimetype='application/json')

            #     userID = None
            #     if 'id' in student:
            #         userID = student['id']
            #         db.execute('UPDATE student SET currentMeeting = %s, joinTime = %s WHERE userID = %s AND confidence > 2 AND currentMeeting <> %s;', (uuid, joinTime, userID, uuid))
            #     #try to indentify student using zoom userID
            #     if db.rowcount <= 0:
            #         #if that doesn't work, try with username
            #         name = student['user_name']
            #         #make name determination more robust

            #         if userID == '' or userID == None:
            #             db.execute('UPDATE student SET currentMeeting = %s, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, joinTime, name, uuid))    
            #         else:
            #             #we know the userID is corret for sure
            #             db.execute('UPDATE student SET currentMeeting = %s, userID = %s, confidence = 3, joinTime = %s WHERE name = %s AND currentMeeting <> %s;', (uuid, userID, joinTime, name, uuid))

            #         #if that doesn't work, STRANGER DANGER
            #         if db.rowcount <= 0:
            #             db.execute('SELECT * FROM student WHERE name = %s OR (userID = %s AND (confidence > 2 OR currentMeeting = %s));', (name, userID, uuid))
            #             if db.rowcount <= 0:
            #                 db.execute('INSERT INTO stranger (userID, currentMeeting, joinTime, name) VALUES (%s, %s, %s, %s);', (userID, uuid, joinTime, name))
            #     db_conn.commit()

            elif event['event'] == 'meeting.started':
                meeting = payload['object']
                uuid = meeting['uuid']
                userID = meeting['host_id']
                startTime = meeting['start_time']
                db.execute('UPDATE teacher SET currentMeeting = %s, startTime = %s WHERE userID = %s AND currentMeeting is NULL;', (uuid, startTime, userID))
                db_conn.commit()

            elif event['event'] == 'meeting.ended':
                meeting = payload['object']
                uuid = meeting['uuid']
                userID = meeting['host_id']

                db.execute('SELECT * FROM teacher WHERE userID = %s;', (userID,))
                account = db.fetchone()

                db.execute('SELECT name FROM stranger WHERE currentMeeting = %s;', (account[2],))
                stranger = []
                for unknown in db:
                    stranger.append(unknown[0])
                
                db.execute('DELETE FROM stranger WHERE currentMeeting = %s;', (account[2],))

                db.execute('SELECT EXTRACT(DOW FROM %s), EXTRACT(HOUR FROM %s), EXTRACT(MINUTE FROM %s);', (account[3], account[3], account[3]))
                time = db.fetchone()
                period, startTime = getPeriod((time[0]-1)*24*60+time[1]*60+time[2])
                if period == 'teacher0':
                    db.execute('UPDATE teacher SET currentMeeting = NULL WHERE userID = %s;', (userID,))
                    db_conn.commit()
                    return Response(status=200, mimetype='application/json')
                # assert that meeting is a class
                
                current_time = datetime.now(timezone.utc)
                meeting_duration = current_time - account[3].astimezone(timezone.utc)
                if meeting_duration.total_seconds() < 180:
                    db.execute('UPDATE teacher SET currentMeeting = NULL WHERE userID = %s;', (userID,))
                    db_conn.commit()
                    return Response(status=200, mimetype='application/json')
                # assert that meeting duration is more than 3 minutes (not a misclick)

                db.execute('SELECT COUNT(*) FROM history WHERE teacher = %s AND period = %s AND EXTRACT(DAY FROM date) = %s;', (account[0], period, current_time.day))
                if db.fetchone()[0] > 0:
                    db.execute('UPDATE teacher SET currentMeeting = NULL WHERE userID = %s;', (userID,))
                    db_conn.commit()
                    return Response(status=200, mimetype='application/json')
                # #assert that only one meeting per period per day

                db.execute('SELECT EXTRACT(DOW FROM joinTime), EXTRACT(HOUR FROM joinTime), EXTRACT(MINUTE FROM joinTime), name, currentMeeting FROM student WHERE {} = %s;'.format(period), (account[0],))
                roster = db.fetchall()
                if len(roster) == 0:
                    db.execute('UPDATE teacher SET currentMeeting = NULL WHERE userID = %s;', (userID,))
                    db_conn.commit()
                    return Response(status=200, mimetype='application/json')
                #assert that there are students in the class
                
                tardy = []
                absent = []

                for student in roster:
                    name = student[3]
                    currentMeeting = student[4]
                    if currentMeeting == account[2] and student[0] != None:
                        #student is in class
                        joinTime = (student[0]-1)*24*60+student[1]*60+student[2]
                        if joinTime-startTime>30:
                            absent.append(name)
                        elif joinTime-startTime>account[5]:
                            tardy.append(name)
                    else:
                        absent.append(name)
                
                #add to history
                db.execute('UPDATE history SET absent = %s, tardy = %s, stranger = %s, date = %s WHERE period = %s AND teacher = %s;', (absent, tardy, stranger, account[3], period, account[0]))
                if db.rowcount <= 0:
                    db.execute('INSERT INTO history (absent, tardy, stranger, date, period, teacher) VALUES (%s, %s, %s, %s, %s, %s);', (absent, tardy, stranger, account[3], period, account[0]))

                db.execute('UPDATE teacher SET currentMeeting = NULL WHERE userID = %s;', (userID,))
                db_conn.commit()

            elif event['event'] == 'app_deauthorized':
                if payload['client_id'] == '9fw3_isjQ2qsfGQqIFSwag':
                    userID = payload['user_id']
                    db.execute('SELECT * FROM teacher WHERE userID = %s;', (userID,))
                    account = db.fetchone()
                    db.execute('UPDATE student SET teacher1 = NULL WHERE teacher1 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher2 = NULL WHERE teacher2 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher3 = NULL WHERE teacher3 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher4 = NULL WHERE teacher4 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher5 = NULL WHERE teacher5 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher6 = NULL WHERE teacher6 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher7 = NULL WHERE teacher7 = %s;', (account[0],))
                    db.execute('UPDATE student SET teacher8 = NULL WHERE teacher8 = %s;', (account[0],))
                    db.execute('DELETE FROM student WHERE teacher1 is NULL AND teacher2 is NULL AND teacher3 is NULL AND teacher4 is NULL AND teacher5 is NULL AND teacher6 is NULL AND teacher7 is NULL AND teacher8 is NULL;')
                    db.execute('DELETE FROM history WHERE teacher = %s;', (account[0],))
                    db.execute('DELETE FROM teacher WHERE userID = %s;', (userID,))
                    db_conn.commit()
                    
            return Response(status=200, mimetype='application/json')
        return Response(status=401, mimetype='application/json')