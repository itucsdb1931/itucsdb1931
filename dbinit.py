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
"INSERT INTO PATIENT VALUES(1000, 'ALI', 13, 50.5, 165, '03/12/2018', 3)",
"INSERT INTO PATIENT VALUES(1001, 'VELI', 12, 45, 130, '05/12/2018', 2)",
"INSERT INTO MEDICAL_DEVICE VALUES(1000, 'GLASSES', 'EYES', 1000)",
"INSERT INTO SURGERY VALUES(1000, 'APANDIS', 'KARIN', 2, 1000)",
"INSERT INTO FAMILY_DISEASE VALUES(1000, 'DIYABET', 'BOBREK', 1000)",
"INSERT INTO MEDICATION VALUES(1000, 'ANTIBIYOTIK', 'SABAH-AKSAM', 1000)",
"INSERT INTO DISCOMFORT VALUES(1000, 'BAS AGRISI', 'KAFA', 3, 1000)",

"INSERT INTO USERS VALUES(1000, 'ozan', '$pbkdf2-sha256$29000$6L3XWqu1du69V6p1TmktxQ$/j/yTWeq/JtoAegueFAAsPEMre0yLL1PVw5Dt1abC.Q', 'ozan@gmail.com', TRUE)",
"INSERT INTO USERS VALUES(1001, 'talha', '$pbkdf2-sha256$29000$Q0jJGcP4PwcAgJDy3nsvZQ$UXWEIRdeKoW0zA//412i/bupIqKUO4lbx5PvPj5izOE', 'talha@gmail.com', FALSE)"


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
