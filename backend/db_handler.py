import mysql.connector
from mysql.connector import Error
from typing import List, Optional, Tuple

# ------------------ CONFIGURATION ------------------

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "@Admin123",
    "database": "db_catalog"  # coordinator node
}

def get_connection():
    """Get connection to the catalog/coordinator database."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Connection error: {e}")
        return None

# ------------------ PROCEDURE CALL HELPERS ------------------

def add_student(roll_no: int, name: str, branch: str, marks: float, attendance: float) -> bool:
    """Call stored procedure add_student() in MySQL."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.callproc("add_student", (roll_no, name, branch, marks, attendance))
        conn.commit()
        return True
    except Error as e:
        print(f"❌ Error in add_student: {e}")
        return False
    finally:
        conn.close()


def update_student(roll_no: int, branch: str, new_marks: float, new_attendance: float) -> bool:
    """Call stored procedure update_student() in MySQL."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.callproc("update_student", (roll_no, branch, new_marks, new_attendance))
        conn.commit()
        return True
    except Error as e:
        print(f"❌ Error in update_student: {e}")
        return False
    finally:
        conn.close()


def delete_student(roll_no: int, branch: str) -> bool:
    """Call stored procedure delete_student() in MySQL."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.callproc("delete_student", (roll_no, branch))
        conn.commit()
        return True
    except Error as e:
        print(f"❌ Error in delete_student: {e}")
        return False
    finally:
        conn.close()


def fetch_all_students() -> List[Tuple]:
    """Fetch all students using the all_students view in db_catalog."""
    conn = get_connection()
    students = []
    if not conn:
        return students
    try:
        cur = conn.cursor()
        cur.execute("SELECT roll_no, name, branch, marks, attendance FROM all_students;")
        students = cur.fetchall()
    except Error as e:
        print(f"⚠ Error fetching students: {e}")
    finally:
        conn.close()
    return students


def filter_students(branch=None, roll_from=None, roll_to=None, marks_min=None, marks_max=None,
                    attendance_min=None, attendance_max=None) -> List[Tuple]:
    """Call stored procedure filter_students() in MySQL."""
    conn = get_connection()
    students = []
    if not conn:
        return students
    try:
        cur = conn.cursor()
        params = tuple(None if v in ("", "All") else v for v in
                       (branch, roll_from, roll_to, marks_min, marks_max, attendance_min, attendance_max))
        cur.callproc("filter_students", params)
        for result in cur.stored_results():
            students.extend(result.fetchall())
    except Error as e:
        print(f"⚠ Error in filter_students: {e}")
    finally:
        conn.close()
    return students

def search_students(keyword: Optional[str] = None,
                    min_marks: Optional[float] = None,
                    max_marks: Optional[float] = None,
                    branch: Optional[str] = None) -> List[Tuple]:
    """Call stored procedure search_students() in MySQL."""
    conn = get_connection()
    results = []
    if not conn:
        return results
    try:
        cur = conn.cursor()
        cur.callproc("search_students", (keyword, min_marks, max_marks, branch))
        for result in cur.stored_results():
            results.extend(result.fetchall())
    except Error as e:
        print(f"⚠ Error in search_students: {e}")
    finally:
        conn.close()
    return results


def setup_databases():
    """Not needed anymore (schema handled by SQL setup)."""
    print("ℹ️ Setup handled directly in MySQL (distributed_backend.sql).")
