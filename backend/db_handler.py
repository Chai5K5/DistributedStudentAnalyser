import mysql.connector, json, threading
from mysql.connector import Error

# Load global metadata
with open("backend/meta_config.json") as f:
    META = json.load(f)

# -------- Connection helpers --------
def get_connection(branch):
    cfg = META.get(branch.upper())
    if not cfg:
        raise ValueError(f"Unknown branch: {branch}")
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"]
    )

def get_all_connections():
    for name, cfg in META.items():
        yield name, mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"]
        )

# -------- Distributed Operations --------
def fetch_all_students():
    """Union of students from every node."""
    students = []
    threads = []

    def fetch_from_node(node, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM students;")
        rows = cur.fetchall()
        students.extend(rows)
        conn.close()

    for name, conn in get_all_connections():
        t = threading.Thread(target=fetch_from_node, args=(name, conn))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    return students

def add_student(roll_no, name, branch, marks, attendance):
    conn = get_connection(branch)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students VALUES (%s,%s,%s,%s,%s)",
            (roll_no, name, branch, marks, attendance)
        )
        conn.commit()
        print(f"✅ Student {name} added to {branch} node.")
    except Error as e:
        if e.errno == 1062:
            print(f"⚠️ Duplicate roll_no {roll_no} — skipping insert.")
        else:
            print("❌ Error adding student:", e)
    finally:
        conn.close()

def search_students(keyword=None, min_marks=None, max_marks=None, branch=None):
    """Example distributed selection & projection using σ conditions."""
    results, threads = [], []
    conditions, params = [], []

    if keyword:
        conditions.append("name LIKE %s")
        params.append(f"%{keyword}%")
    if min_marks is not None:
        conditions.append("marks >= %s")
        params.append(min_marks)
    if max_marks is not None:
        conditions.append("marks <= %s")
        params.append(max_marks)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    def run_query(conn):
        cur = conn.cursor()
        cur.execute(f"SELECT roll_no, name, branch, marks, attendance FROM students {where};", params)
        results.extend(cur.fetchall())
        conn.close()

    if branch:
        conn = get_connection(branch)
        run_query(conn)
    else:
        for _, conn in get_all_connections():
            t = threading.Thread(target=run_query, args=(conn,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    return results
