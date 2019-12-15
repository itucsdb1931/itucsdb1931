import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
"INSERT INTO BLOOD_TYPE VALUES(1, 'AB', '+')",
"INSERT INTO BLOOD_TYPE VALUES(2, 'AB', '-')",
"INSERT INTO BLOOD_TYPE VALUES(3, '0', '+')",
"INSERT INTO BLOOD_TYPE VALUES(4, '0', '-')",
"INSERT INTO BLOOD_TYPE VALUES(5, 'A', '+')",
"INSERT INTO BLOOD_TYPE VALUES(6, 'A', '-')",
"INSERT INTO BLOOD_TYPE VALUES(7, 'B', '+')",
"INSERT INTO BLOOD_TYPE VALUES(8, 'B', '-')",
"INSERT INTO PATIENT VALUES(1, 'ALI', 13, 50.5, 165, '20.12.2018', 3)",
"INSERT INTO PATIENT VALUES(2, 'VELI', 12, 45, 130, '05.12.2018', 2)",
"INSERT INTO MEDICAL_DEVICE VALUES(1, 'GLASSES', 'EYES', 1)",
"INSERT INTO SURGERY VALUES(1, 'APANDIS', 'KARIN', 2, 1)",
"INSERT INTO FAMILY_DISEASE VALUES(1, 'DIYABET', 'BOBREK', 1)",
"INSERT INTO MEDICATION VALUES(1, 'ANTIBIYOTIK', 'SABAH-AKSAM', 1)",
"INSERT INTO DISCOMFORT VALUES(1, 'BAS AGRISI', 'KAFA', 3, 1)",
"INSERT INTO USERS VALUES(1, 'ozan', 'ozan', 'ozan@gmail.com', TRUE)",
"INSERT INTO USERS VALUES(2, 'talha', 'talha', 'talha@gmail.com', FALSE)"
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
