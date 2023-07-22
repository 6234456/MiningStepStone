# -*- coding: <utf-8> -*-


# author:    Qiou Yang
# email:     sgfxqw@gmail.com
# desc:      Web-GUI to interact with user

import datetime
import os
import re
import urllib.parse
from json import dumps

from flask import Flask, render_template, request

import cfg
import emailUtil
from ORM import DBUtil, Job, StatutsVeraenderung, entryAdapter
from docTemplateEngine import render, parseText
from extraction import mining

app = Flask(__name__)
db = DBUtil()
cfginfo = cfg.info()

@app.route("/")
def hello():
    return render_template("main.html")

@app.route("/jobs")
def jobs():
    db.openSession()
    data = [i.toDict() for i in db.session.query(Job).filter(Job.geloescht==False).all()]
    return dumps(data)

@app.route("/status")
def status():
    db.openSession()
    return dumps(db.process_StatusCode())

@app.route("/add", methods=['POST'])
def add():
    db.openSession()
    url = urllib.parse.unquote(request.form.get('url'))
    db.add_all(mining(url), entryAdapter)
    db.commit()
    return "OK"

@app.route("/change", methods=['POST'])
def change():
    db.openSession()
    job = request.get_json()

    del job['status']
    del job['arbeitgeber']

    old_job = db.byID(job['id'], Job)
    job['eingetragen_am'] = old_job.eingetragen_am

    if job['status_id'] != old_job.status_id:
        #if status changed
        db.add(StatutsVeraenderung(**{'veraendert_am' : datetime.datetime.now(), 'status_id' : job['status_id']}))

    db.session.delete(old_job)
    db.add(Job(**job))

    db.commit()
    return "OK"

@app.route("/send", methods=['POST'])
def send():
    if not (cfginfo['email_usr'] and cfginfo['email_pwd']):
        raise ValueError("Bitte zuerst Zugangsdata in cfg.py festlegen!")
    else:
        db.openSession()
        targ = request.get_json()

        obj = db.session.query(Job).filter(Job.id==targ['targ']).one()
        if obj:
            # set status to 101
            if obj.status_id == 100:
                obj.status_id = 101

            # generate doku
            emailBodyText = __prepareDoku(obj)

            # send email
            emailUtil.send(cfginfo['email_usr'], cfginfo['email_pwd'], obj.email.strip(),
                           "Bewerbung um eine Arbeitsplatz als " + obj.name, emailBodyText, cfginfo['email_smtp_server'],
                           cfginfo['email_smtp_server_port'], [re.sub("[\$\\\/\-\&]", "_", obj.arbeitgeber.name)+"/" + cfginfo['name_datei_anschreiben'], cfginfo['path_document']])
            db.commit()

    return "OK"

@app.route("/delete", methods=['POST'])
def delete():
    db.openSession()
    targ = request.get_json()

    obj = db.session.query(Job).filter(Job.id==targ['targ']).one()

    if obj:
        obj.geloescht = True
        obj.geloescht_am = datetime.datetime.now()

        db.commit()
    else:
        return "Fail"

    return "OK"

@app.route("/doku", methods=['POST'])
def doku():
    db.openSession()
    targ = request.get_json()
    obj = db.session.query(Job).filter(Job.id==targ['targ']).one()

    __prepareDoku(obj)

    return "OK"


def __prepareDoku(obj):
    # prepare the info to fill in the template
    anrede_dict = {
        'M' : ['Herr', 'Sehr geehrter Herr'],
        'F' : ['Frau', 'Sehr geehrte Frau'],
        'N/A' : ['Human Resources', 'Sehr geehrte Damen und Herren,'],
    }

    # German locale not installed
    monthName = {
        1 : "Januar", 2 :"Februar", 3:"März", 4:"April", 5:"Mai", 6 :"Juni",
        7 : "Juli", 8: "August", 9 : "September", 10 : "Oktober", 11 : "November", 12: "Dezember"
    }
    if obj:
        d = obj.toDict()
        if d['anrede']:
            tmp = anrede_dict[d['anrede']]

            if d['ansp_vor']:
                d['ansprechpartner_address'] = tmp[0] + " " + d['ansp_vor'] + " " + d['ansp_nach']
            else:
                d['ansprechpartner_address'] = tmp[0] + " " + d['ansp_nach']

            d['brief_anrede'] = tmp[1] + " " + d['ansp_nach'] + ","
        else:
            d['ansprechpartner_address'] = anrede_dict['N/A'][0]
            d['brief_anrede'] = anrede_dict['N/A'][1]

        td = datetime.date.today()
        d['date'] = str(td.day) + "." + monthName[td.month] + " " + str(td.year)

        # generate file in the path
        pName = re.sub("[\$\\\/\-\&]", "_", obj.arbeitgeber.name)

        if not os.path.isdir(pName):
            os.mkdir(pName)

        render(d, cfginfo['path_template_anschreiben'], pName + "/" + cfginfo['name_datei_anschreiben'])
        return parseText(d, cfginfo['path_template_email_text'])
    else:
        raise TypeError

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')