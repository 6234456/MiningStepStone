# -*- coding: <utf-8> -*-


# author:    Qiou Yang
# email:     sgfxqw@gmail.com
# desc:      Web-GUI to interact with user

from json import dumps
from flask import Flask, render_template, request
from ORM import DBUtil, Job, StatutsVeraenderung, entryAdapter
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')