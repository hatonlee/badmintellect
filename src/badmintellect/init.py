import sqlite3
import sys
import random
from time import time
from datetime import datetime, timedelta

def run_schema(cursor):
    start_time = time()

    try:
        with open("schema.sql", "r") as f:
            schema_script = f.read()
            cursor.executescript(schema_script)
    except (FileNotFoundError, sqlite3.OperationalError):
        return "[ ERROR ] schema.sql"

    end_time = time()
    result = end_time - start_time
    return f"[ OK ] schema.sql ({result:.3f}s)"

def run_index(cursor):
    start_time = time()

    try:
        with open("index.sql", "r") as f:
            index_script = f.read()
            cursor.executescript(index_script)
    except (FileNotFoundError, sqlite3.OperationalError):
        return "[ ERROR ] index.sql"

    end_time = time()
    result = end_time - start_time
    return f"[ OK ] index.sql ({result:.3f}s)"

def run_init(cursor):
    start_time = time()

    try:
        with open("init.sql", "r") as f:
            init_script = f.read()
            cursor.executescript(init_script)
    except (FileNotFoundError, sqlite3.OperationalError):
        return "[ ERROR ] init.sql"

    end_time = time()
    result = end_time - start_time
    return f"[ OK ] init.sql ({result:.3f}s)"

def give_badmin(cursor):
    start_time = time()
    sql = """UPDATE users
                SET user_role = 'badmin'"""

    cursor.execute(sql)
    end_time = time()
    result = end_time - start_time
    return f"[ OK ] badmin ({result:.3f}s)"

def create_test_data(cursor, user_count=10**3, reservation_count=10**5, comment_count=10**6, enrollment_count=10**5):
    start_time = time()

    epoch = datetime(1970, 1, 1)
    now = datetime.now()

    try:
        sql = """INSERT INTO users (username)
                 VALUES (?)"""

        for i in range(1, user_count + 1):
                cursor.execute(sql, (f"user{i}",))

        sql = """INSERT INTO reservations (user_id, title, place, date, time, duration)
                 VALUES (?, ?, ?, ?, ?, ?)"""

        for i in range(1, reservation_count + 1):
            # random date
            seconds = random.randint(0, int((now - epoch).total_seconds()))
            random_date = (epoch + timedelta(seconds=seconds)).strftime("%Y-%m-%d")

            # random time of day
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            random_time = f"{hours:02}:{minutes:02}"

            # random duration
            minutes = 30 * random.randint(0, 6)
            hours = minutes // 60
            minutes = minutes - 60 * hours
            random_duration = f"{hours:02}:{minutes:02}"

            cursor.execute(sql, (random.randint(1, user_count), f"Title {i}", "Random place", random_date, random_time, random_duration))

        sql = """INSERT INTO comments (user_id, reservation_id, comment, post_time)
                 VALUES (?, ?, ?, ?)"""

        for _ in range(1, comment_count + 1):
            # random datetime
            seconds = random.randint(0, int((now - epoch).total_seconds()))
            random_datetime = (epoch + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M")
            cursor.execute(sql, (random.randint(1, user_count), random.randint(1, reservation_count), f"Comment {i}", random_datetime))

        sql = """INSERT INTO enrollments (user_id, reservation_id)
                      VALUES (?, ?)"""

        for i in range(1, enrollment_count + 1):
            try:
                cursor.execute(sql, (random.randint(1, user_count), random.randint(1, reservation_count)))
            except sqlite3.IntegrityError:
                pass

    except sqlite3.IntegrityError:
        return "[ ERROR ] testdata"

    end_time = time()
    result = end_time - start_time
    return f"[ OK ] testdata ({result:.3f}s)"

def show_performance_results():
    performance_results = """
App tested with the following datasets
User count: 10 ** 3
Reservation count: 10 ** 5
Comment count: 10 ** 6
Enrollment count: 10 ** 4

Load times:
Front page: ms
Search: 40ms with all parameters

User count: 10 ** 4
Reservation count: 10 ** 5
Comment count: 10 ** 8
Enrollment count: 10 ** 5

Load times:
Front page: 60ms
Search: 100ms with all parameters"""

    print(performance_results)

def init_cli():
    action = input(">>> ")

    con = sqlite3.connect("database.db")
    cursor = con.cursor()

    match action:
        case "8":
            con.close()
            sys.exit()
        case "7":
            show_performance_results()
        case "6":
            print(give_badmin(cursor))
        case "5":
            print(run_schema(cursor))
            print(run_init(cursor))
            print(create_test_data(cursor))
            print(run_index(cursor))
        case "4":
            print(create_test_data(cursor))
        case "3":
            print(run_init(cursor))
        case "2":
            print(run_index(cursor))
        case "1":
            print(run_schema(cursor))
        case _:
            print("[ ERROR ] Not a valid command")

    con.commit()
    con.close()

if __name__ == "__main__":
    prompt = """
--- App init tool ---
[1] Run schema.sql (DROPS EVERYTHING)
[2] Run index.sql (recommended after creating test data)
[3] Run init.sql
[4] Create test data
[5] Run 1 - 4
[6] Give badmin role to all users (development only)
[7] Show performance test results
[8] Exit"""

    print(prompt)
    while True:
        init_cli()