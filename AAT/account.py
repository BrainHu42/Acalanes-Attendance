import pip._vendor.requests as requests
import openpyxl
import re
from pathlib import Path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from datetime import datetime
from werkzeug.exceptions import abort

from AAT.auth import login_required
from AAT.db import get_db

bp = Blueprint('account', __name__, url_prefix='/account')

def getPeriod():
    weekday = datetime.today().weekday()
    time = datetime.now().hour*60+datetime.now().minute
    teacher = 'teacher0'
    if weekday==1 or weekday==3:
        if time>540 and time<615:
            teacher = 'teacher1'
        elif time>630 and time<705:
            teacher = 'teacher2'
        elif time>750 and time<825:
            teacher = 'teacher3'
        elif time>840 and time<915:
            teacher = 'teacher7'
    elif weekday==2 or weekday==4:
        if time>600 and time<675:
            teacher = 'teacher4'
        elif time>690 and time<765:
            teacher = 'teacher5'
        elif time>810 and time<885:
            teacher = 'teacher6'
    elif weekday==0:
        if time>540 and time<585:
            teacher = 'teacher8'
    
    if teacher == 'teacher0':
        teacher = 'teacher7'

    return teacher

@bp.route('/admit/<userID>', methods=('GET', 'POST'))
@login_required
def admit(userID):
    if request.method == 'POST':
        student = request.form['student']
        db_conn = get_db()
        db = db_conn.cursor()
        period = getPeriod()
        account = g.user

        db.execute('UPDATE student SET userID = %s, currentMeeting = %s WHERE name = %s;', (userID, account[2], student))
        db.execute('DELETE FROM stranger WHERE userID = %s;', (userID,))
        db_conn.commit()
        return redirect(url_for('account.details'))

    elif request.method == 'GET':
        db_conn = get_db()
        db = db_conn.cursor()
        period = getPeriod()
        account = g.user

        db.execute('SELECT * FROM stranger WHERE userID = %s;', (userID,))
        stranger = db.fetchone()

        db.execute('SELECT name FROM student WHERE {} = %s AND currentMeeting != %s AND userID is NULL;'.format(period), (account[0], stranger[1]))
        unassigned = db.fetchall()
        length = len(unassigned)
        #add new student
        if length == 0:
            db.execute('INSERT INTO student (currentMeeting, name, {}, userID) VALUES (%s, %s, %s, %s);'.format(period), (stranger[1], stranger[2], account[0], userID))
        elif length == 1:
            db.execute('UPDATE student SET userID = %s, currentMeeting = %s WHERE name = %s;', (userID, stranger[1], unassigned[0][0]))
        else:
            return render_template('account/option.html', stranger=stranger[2], students=unassigned)
        
        db.execute('DELETE FROM stranger WHERE userID = %s;', (userID,))
        db_conn.commit()
        return redirect(url_for('account.details'))


@bp.route('/reject/<userID>', methods=('GET',))
@login_required
def reject(userID):
    db_conn = get_db()
    db = db_conn.cursor()
    db.execute('DELETE FROM stranger WHERE userID = %s;', (userID,))
    db_conn.commit()
    return redirect(url_for('account.details'))

@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == 'POST':
        email = g.user[0]
        db_conn = get_db()
        db = db_conn.cursor()
        uploaded_file = request.files['upload-file']
        file_sheet = openpyxl.load_workbook(uploaded_file).active
        row_index = 1
        
        while row_index < file_sheet.max_row:
            if file_sheet.cell(row=row_index, column=1).value=="Period":
                period = file_sheet.cell(row=row_index+1, column=1).value
                row_index+=4
                temp = row_index
                while file_sheet.cell(row=row_index, column=5).value!=None:
                    words = re.findall(r"[\w']+", file_sheet.cell(row=row_index, column=5).value)
                    name = words[1]+" "+words[0]
                    db.execute('UPDATE student SET {} = %s WHERE name = %s;'.format("teacher"+period), (email, name))
                    if db.rowcount == 0:
                        db.execute(
                            'INSERT INTO student (currentMeeting, name, {}) VALUES (%s, %s, %s);'.format("teacher"+period),
                            ("area51",name, email)
                        )
                    row_index += 1
                #nothing happened so try column 4
                if row_index == temp:
                    while file_sheet.cell(row=row_index, column=4).value!=None:
                        words = re.findall(r"[\w']+", file_sheet.cell(row=row_index, column=4).value)
                        name = words[1]+" "+words[0]
                        db.execute('SELECT count(*) FROM student WHERE name = %s;',(name,))
                        if db.fetchone()[0]>0:
                            db.execute('UPDATE student SET {} = %s WHERE name = %s;'.format("teacher"+period), (email, name))
                        else:
                            db.execute(
                                'INSERT INTO student (currentMeeting, name, {}) VALUES (%s, %s, %s);'.format("teacher"+period),
                                ("area51",name, email)
                            )
                        row_index += 1
            else:
                row_index += 1
        db_conn.commit()
        return redirect(url_for('account.details'))
    
    return render_template('account/settings.html')

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def details():
    db = get_db().cursor()
    account = g.user
    period = getPeriod()

    db.execute('SELECT * FROM stranger WHERE currentMeeting = %s;', (account[2],))
    stranger_danger = db.fetchall()

    db.execute('SELECT name FROM student WHERE {} = %s AND currentMeeting != %s;'.format(period), (account[0], account[2]))
    naughty_list = db.fetchall()

    return render_template('account/dashboard.html', period=period[-1:], absent=naughty_list, stranger=stranger_danger)