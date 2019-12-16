import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
"CREATE TABLE IF NOT EXISTS USERS(ID SERIAL PRIMARY KEY, USERNAME VARCHAR(255), PASSWORD VARCHAR(255), MAIL VARCHAR(255), ISADMIN BOOL DEFAULT FALSE)",
    "CREATE TABLE IF NOT EXISTS BLOOD_TYPE(ID SERIAL PRIMARY KEY, TYPE VARCHAR(2), RH CHAR(1))",
    "CREATE TABLE IF NOT EXISTS PATIENT(ID SERIAL PRIMARY KEY, NAME VARCHAR(30), AGE INTEGER, WEIGHT FLOAT, HEIGHT FLOAT, LAST_EXAMINATION_DATE DATE, BLOOD_TYPE INTEGER REFERENCES BLOOD_TYPE(ID))",
    "CREATE TABLE IF NOT EXISTS ALLERGY(ID SERIAL PRIMARY KEY, NAME VARCHAR(40), AREA VARCHAR(25), PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS MEDICAL_DEVICE(ID SERIAL PRIMARY KEY, NAME VARCHAR(40), AREA VARCHAR(25), PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS SURGERY(ID SERIAL PRIMARY KEY, NAME VARCHAR(40), AREA VARCHAR(25), LEVELS INTEGER, PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS FAMILY_DISEASE(ID SERIAL PRIMARY KEY, NAME VARCHAR(40), AREA VARCHAR(25), PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS MEDICATION(ID SERIAL PRIMARY KEY, NAME VARCHAR(25), USAGES VARCHAR(25), PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)",
    "CREATE TABLE IF NOT EXISTS DISCOMFORT(ID SERIAL PRIMARY KEY, NAME VARCHAR(25), AREA VARCHAR(25), LEVELS INTEGER, PERSON INTEGER REFERENCES PATIENT ON DELETE CASCADE)"

]

def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
