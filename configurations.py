import os.path
import sys

DSN_tc = {'user': "postgres",
           'password': "123",
           'host': "127.0.0.1",
           'port': "5432",
           'database': "dummy"
           }

DSN_dok = {'user': "postgres",  #
          'password': "proje317",
          'host': "127.0.0.1",
          'port': "5432",
          'database': "postgres"
          }

#  postgres//user:pw@host:port/database

tc_connection_url = "dbname={} user={} password={} host={} port={}".format(DSN_tc['database'], DSN_tc['user'],
                                                                           DSN_tc['password'], DSN_tc['host'],
                                                                           DSN_tc['port'])

dok_connection_url = "dbname={} user={} password={} host={} port={}".format(DSN_dok['database'], DSN_dok['user'],
                                                                            DSN_dok['password'], DSN_dok['host'],
                                                                            DSN_dok['port'])
HOME_PATH = os.path.expanduser("~").lower()  # home url of pc
db_url = str()

try:
    if 'talha' in HOME_PATH:  # Pc of TALHA ÇOMAK
        db_url = tc_connection_url
    elif 'oziku' in HOME_PATH:  # Pc of DOĞU OZAN KUMRU
        db_url = dok_connection_url
    elif 'app' in HOME_PATH:  # Heroku
        db_url = os.getenv("DATABASE_URL")
except Exception as e:
    print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
    sys.exit(1)