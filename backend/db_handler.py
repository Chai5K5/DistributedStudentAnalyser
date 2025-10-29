# backend/db_handler.py
import mysql.connector
from mysql.connector import Error

# Connections to both databases
def connect_cse():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Admin123",
        database="db_cse"
    )

def connect_aiml():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Admin123",
        database="db_aiml"
    )

def get_connection(branch):
    """Return connection to correct database based on branch."""
    if branch.upper() == "CSE":
        return connect_cse()
    elif branch.upper() == "AIML":
        return connect_aiml()
    else:
        raise ValueError(f"Unknown branch: {branch}")

def fetch_all_students():
    """Fetch all students from both nodes."""
    students = []
    try:
        conn_cse = connect_cse()
        conn_aiml = connect_aiml()
        cur_cse = conn_cse.cursor()
        cur_aiml = conn_aiml.cursor()
        cur_cse.execute("SELECT * FROM students;")
        cur_aiml.execute("SELECT * FROM students;")
        students.extend(cur_cse.fetchall())
        students.extend(cur_aiml.fetchall())
    finally:
        if conn_cse.is_connected():
            conn_cse.close()
        if conn_aiml.is_connected():
            conn_aiml.close()
    return students

# ------------------ CRUD FUNCTIONS ------------------

def add_student(roll_no, name, branch, marks, attendance):
    """Insert a new student into correct node."""
    conn = get_connection(branch)
    try:
        cursor = conn.cursor()
        query = "INSERT INTO students (roll_no, name, branch, marks, attendance) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (roll_no, name, branch, marks, attendance))
        conn.commit()
        return True
    except Error as e:
        print("❌ Error adding student:", e)
        return False
    finally:
        conn.close()

def update_student(roll_no, branch, new_marks, new_attendance):
    """Update marks/attendance for a student."""
    conn = get_connection(branch)
    try:
        cursor = conn.cursor()
        query = "UPDATE students SET marks=%s, attendance=%s WHERE roll_no=%s"
        cursor.execute(query, (new_marks, new_attendance, roll_no))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print("❌ Error updating student:", e)
        return False
    finally:
        conn.close()

def delete_student(roll_no, branch):
    """Delete a student from correct node."""
    conn = get_connection(branch)
    try:
        cursor = conn.cursor()
        query = "DELETE FROM students WHERE roll_no=%s"
        cursor.execute(query, (roll_no,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print("❌ Error deleting student:", e)
        return False
    finally:
        conn.close()
