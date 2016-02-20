# run once to migrate the database before the first time to launch the server

from ORM import DBUtil

if __name__ == '__main__':
    db = DBUtil()
    db.initialize()