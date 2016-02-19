# -*- coding: <utf-8> -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
import datetime

Base = declarative_base()

desc_status = '''
        100 - Unbeworben

        200 - Zusagen
        201 - zum Vorstellungsgespräche eingeladen
        202 - Eingangsbestätigung erhalten
        203 - zum Telefoninterview eingeladen

        300 - Eingangsbestätigung Vermittler
        301 - zum Telefoninterview eingeladen Vermittler
        302 - zum Vorstellungsgespräche eingeladen durch Vermittler

        400 - Telefoninterview abgesagt (vom Bewerber) außer 402
        401 - Vorstellungsgespräche abgesagt (vom Bewerber) außer 402
        402 - Absagen wegen nicht-Erstattung der Fahrtkosten (vom Bewerber)
        403 - Bewerbung zurückgezogen

        500 - keine Rückmeldung in 15 Tage
        501 - keine Rückmeldung in 30 Tage
        502 - Stelle veraltet
        503 - Ausschreibung zurückgezogen
        504 - Absagen
    '''

class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    plz = Column(String)
    stadt = Column(String)
    strasse = Column(String)
    durch_email = Column(Boolean)
    email = Column(String)
    bemerkung = Column(String, default="")
    eintritt = Column(Boolean)
    gehalt = Column(Boolean)
    status_id = Column(Integer, ForeignKey('status.id'), default=100)
    status = relationship("Bewerbungsstatus", backref=backref('jobs', order_by=id))
    eingetragen_am = Column(DateTime)

    geloescht = Column(Boolean, default=False)
    geloescht_am = Column(DateTime, default=None)

    arbeitgeber = relationship("Arbeitgeber", backref=backref('jobs', order_by=id))
    ag_id = Column(Integer, ForeignKey('arbeitgeber.id'))

class Bewerbungsstatus(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True)
    beschreibung = Column(String)

class StatutsVeraenderung(Base):
    __tablename__ = "statusveraenderung"

    id = Column(Integer, primary_key=True)
    veraendert_am = Column(DateTime)
    status_id = Column(Integer, ForeignKey('status.id'))
    status = relationship("Bewerbungsstatus", backref=backref('changes', order_by=id))


class Arbeitgeber(Base):
    '''
    an employer can have more than one addresses and offer more than one jobs
    '''
    __tablename__ = "arbeitgeber"

    id = Column(Integer, primary_key=True)
    name = Column(String)

def entryAdapter(info):
    '''
    :param info: the mined dict object
    :return: ORM Class mapped to the database
    '''
    j = Job()
    j.ag_id = int(info['agID'])
    j.name = info['job']
    j.id = int(info['jobID'])

    j.eintritt = info['eintrittstermin']
    j.gehalt = info['gehaltsvorstellung']

    j.stadt = info['stadt']
    j.plz = info['plz']

    j.strasse = info['strasse']

    j.url = info['url']
    j.durch_email = info['istDurchEmail']
    j.email = info['email']

    j.eingetragen_am = datetime.datetime.now()

    a = Arbeitgeber()
    a.id = j.ag_id
    a.name = info['arbeitgeber']

    return [j, a]

class DBUtil:
    def __init__(self, url=None):
        if url is None:
            url = "sqlite:///database.db"

        self.db = url
        self.engine = create_engine(url, echo=True)
        self.session = None

    def initialize(self):
        Base.metadata.create_all(self.engine)

        # init of status
        l = []
        for i in desc_status.split("\n"):
            if len(i.strip()) > 0:
                tmp = i.split("-")
                l.append({'id': int(tmp[0].strip()), 'beschreibung': tmp[1].strip()})

        self.openSession()
        self.session.add_all([Bewerbungsstatus(**i) for i in l])
        self.commit()


    def openSession(self):
        if self.session is None:
            self.session = sessionmaker(bind=self.engine)()

    def add_all(self, entry, adaptor):
        self.openSession()

        # integrity check
        obj = adaptor(entry)
        ag_count = self.session.query(Arbeitgeber).filter(Arbeitgeber.id == obj[1].id).count()
        if ag_count == 0:
            self.session.add_all(obj)
        else:
            job_count = self.session.query(Job).filter(Job.id == obj[0].id).count()
            if job_count == 0:
                self.session.add(obj[0])
            elif job_count == 1 and obj[0].geloescht:
                obj[0].geloescht = False
                obj[0].geloescht_am = None
                self.session.add(obj[0])

    def add(self, obj):
        self.openSession()
        self.session.add(obj)

    def commit(self):
        self.session.commit()


if __name__ == '__main__':
    # engine = create_engine("sqlite:///database.db", echo=True)
    # Base.metadata.create_all(engine)

    from extraction import mining

    db = DBUtil()
    # db.initialize()

    db.add_all(mining('http://www.stepstone.de/stellenangebote--Assistent-im-Bereich-Marketing-Communications-m-w-Heilbronn-GGB-Heilbronn-GmbH--3651790-inline.html'),entryAdapter)
    db.commit()