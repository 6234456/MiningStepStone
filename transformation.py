# -*- coding: <utf-8> -*-

'''
Web-GUI to
Database IO
'''

from json import dumps, loads
from flask import Flask, render_template, request
from ORM import DBUtil, Job, Arbeitgeber, Bewerbungsstatus, StatutsVeraenderung, entryAdapter
from extraction import mining
import datetime

app = Flask(__name__)
db = DBUtil()

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
    url = request.form.get('url')
    db.add_all(mining(url), entryAdapter)
    db.commit()
    return "OK"

@app.route("/change", methods=['POST'])
def change():
    db.openSession()
    job = loads(request.form.get('job'))
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')