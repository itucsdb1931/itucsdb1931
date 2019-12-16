import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
"DROP TABLE IF EXISTS PATIENT CASCADE",
"DROP TABLE IF EXISTS MEDICAL_DEVICE",
"DROP TABLE IF EXISTS SURGERY",
"DROP TABLE IF EXISTS FAMILY_DISEASE",
"DROP TABLE IF EXISTS MEDICATION",
"DROP TABLE IF EXISTS DISCOMFORT",
"DROP TABLE IF EXISTS BLOOD_TYPE",
"DROP TABLE IF EXISTS USERS",
"DROP TABLE IF EXISTS ALLERGY",
"DROP TABLE IF EXISTS USERS"

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
