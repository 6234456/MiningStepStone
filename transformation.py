# -*- coding: <utf-8> -*-

'''
Web-GUI to
Database IO
'''

from json import dumps
from flask import Flask, render_template, request
from ORM import DBUtil, Job, Arbeitgeber, Bewerbungsstatus, StatutsVeraenderung, entryAdapter
from extraction import mining

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

@app.route("/add", methods=['POST'])
def add():
    db.openSession()
    url = request.form.get('url')
    db.add_all(mining(url), entryAdapter)
    db.commit()
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')