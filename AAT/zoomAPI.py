import json
import re
import pip._vendor.requests as requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, request, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from AAT.db import get_db

bp = Blueprint('zoomAPI', __name__)

def jprint(obj):
    data = json.dumps(obj, indent=4, sort_keys=True)
    print(data)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        if request.headers['authorization' ] == 'yvbmRQ61SEOCGHSFC6Adtw':
            event = request.json
            payload = event['payload']
            db_conn = get_db()
            db = db_conn.cursor()
            if event['event'] == 'meeting.participant_admitted':
                admitted = payload['object']
                student = admitted['participant']
                uuid = admitted['uuid']
                userID = None
                if 'id' in student:
                    userID = student['id']
                    db.execute('UPDATE student SET currentMeeting = %s WHERE userID = %s;', (uuid, userID))
                #try to indentify student using zoom userID
                if db.rowcount == 0:
                    #if that doesn't work, try with username
                    userName = student['user_name']
                    words = re.findall(r"[\w']+", userName)
                    name = words[0]+" "+words[1]
                    db.execute('UPDATE student SET currentMeeting = %s, userID = %s WHERE name = %s;', (uuid, userID, name))

                    #if that doesn't work, STRANGER DANGER
                    if db.rowcount == 0:
                        db.execute('INSERT INTO stranger (userID, currentMeeting, name) VALUES (%s, %s, %s);', (userID, uuid, userName))
                db_conn.commit()

            elif event['event'] == 'meeting.started':
                meeting = payload['object']
                uuid = meeting['uuid']
                userID = meeting['host_id']
                db.execute('UPDATE teacher SET currentMeeting = %s WHERE userID = %s;', (uuid, userID))
                db_conn.commit()

            elif event['event'] == 'meeting.ended':
                meeting = payload['object']
                uuid = meeting['uuid']
                db.execute('DELETE FROM stranger WHERE currentMeeting = %s;', (uuid,))
                db_conn.commit()
            elif event['event'] == 'meeting.participant_left':
                print('student left')
            return Response(status=200, mimetype='application/json')
        
        return Response(status=401, mimetype='application/json')
    return redirect(url_for('auth.login'))