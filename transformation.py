# -*- coding: <utf-8> -*-

'''
Web-GUI to
Database IO
'''

from json import dumps
from flask import Flask, render_template
from ORM import DBUtil, Job, Arbeitgeber, Bewerbungsstatus, StatutsVeraenderung, entryAdapter

app = Flask(__name__)
db = DBUtil()

@app.route("/")
def hello():
    return render_template("main.html")

@app.route("/jobs")
def jobs():
    db.openSession()
    data = [i.toDict() for i in db.session.query(Job).filter(True).all()]
    return dumps(data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')