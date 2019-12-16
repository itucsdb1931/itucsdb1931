import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
"DELETE FROM USERS WHERE NAME='ozan'",
"DELETE FROM USERS WHERE NAME='talha'",

"INSERT INTO USERS VALUES(1, 'ozan', '$pbkdf2-sha256$29000$6L3XWqu1du69V6p1TmktxQ$/j/yTWeq/JtoAegueFAAsPEMre0yLL1PVw5Dt1abC.Q', 'ozan@gmail.com', TRUE)",
"INSERT INTO USERS VALUES(2, 'talha', '$pbkdf2-sha256$29000$Q0jJGcP4PwcAgJDy3nsvZQ$UXWEIRdeKoW0zA//412i/bupIqKUO4lbx5PvPj5izOE', 'talha@gmail.com', FALSE)"

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
