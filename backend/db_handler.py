import mysql.connector
from mysql.connector import Error
import json
import os

# ------------------ Connection Config ------------------

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "meta_config.json")

# Default metadata file if not found
DEFAULT_META = {
    "nodes": {
        "CSE": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_cse"},
        "AIML": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_aiml"},
        "DS": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_ds"},
        "CC": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_cc"}
    },
    "replication_enabled": False
}


def load_meta():
    """Load distributed metadata configuration."""
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_META, f, indent=4)
        return DEFAULT_META
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


META = load_meta()

# ------------------ Connection Utilities ------------------

def connect_to_node(branch):
    """Connect to the MySQL node for the given branch."""
    branch = branch.upper()
    if branch not in META["nodes"]:
        raise ValueError(f"Unknown branch: {branch}")
    config = META["nodes"][branch]
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"❌ Connection error ({branch}):", e)
        return None


def get_all_connections():
    """Return a dictionary of active connections to all nodes."""
    connections = {}
    for branch in META["nodes"]:
        conn = connect_to_node(branch)
        if conn:
            connections[branch] = conn
    return connections


# ------------------ CRUD Operations ------------------

def add_student(roll_no, name, branch, marks, attendance):
    """Insert student into correct node, replicate if enabled."""
    branch = branch.upper()
    conn = connect_to_node(branch)
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (roll_no, name, branch, marks, attendance) VALUES (%s, %s, %s, %s, %s)",
            (roll_no, name, branch, marks, attendance)
        )
        conn.commit()

        # Replicate if enabled
        if META.get("replication_enabled", False):
            replicate_to_others(roll_no, name, branch, marks, attendance)

        return True
    except Error as e:
        print(f"❌ Error adding student ({branch}):", e)
        return False
    finally:
        conn.close()


def replicate_to_others(roll_no, name, branch, marks, attendance):
    """Replicate student record to all other nodes."""
    for other_branch in META["nodes"]:
        if other_branch == branch:
            continue
        conn = connect_to_node(other_branch)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            cur.execute(
                "REPLACE INTO students (roll_no, name, branch, marks, attendance) VALUES (%s, %s, %s, %s, %s)",
                (roll_no, name, branch, marks, attendance)
            )
            conn.commit()
        except Error as e:
            print(f"⚠ Replication to {other_branch} failed:", e)
        finally:
            conn.close()


def update_student(roll_no, branch, new_marks, new_attendance):
    """Update student record in its respective node."""
    branch = branch.upper()
    conn = connect_to_node(branch)
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET marks=%s, attendance=%s WHERE roll_no=%s",
            (new_marks, new_attendance, roll_no)
        )
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"❌ Error updating student ({branch}):", e)
        return False
    finally:
        conn.close()


def delete_student(roll_no, branch):
    """Delete student record from respective node."""
    branch = branch.upper()
    conn = connect_to_node(branch)
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE roll_no=%s", (roll_no,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"❌ Error deleting student ({branch}):", e)
        return False
    finally:
        conn.close()


# ------------------ Distributed Queries ------------------

def fetch_all_students():
    """Fetch students from all nodes."""
    all_students = []
    connections = get_all_connections()
    for branch, conn in connections.items():
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM students;")
            rows = cur.fetchall()
            all_students.extend(rows)
        except Error as e:
            print(f"⚠ Error fetching from {branch}:", e)
        finally:
            conn.close()
    return all_students


def search_students(keyword=None, min_marks=None, max_marks=None, branch=None):
    """Search across distributed nodes with filters (relational algebra style)."""
    results = []
    target_nodes = [branch.upper()] if branch else list(META["nodes"].keys())

    for node in target_nodes:
        conn = connect_to_node(node)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            query = "SELECT * FROM students WHERE 1=1"
            params = []

            if keyword:
                query += " AND name LIKE %s"
                params.append(f"%{keyword}%")
            if min_marks is not None:
                query += " AND marks >= %s"
                params.append(min_marks)
            if max_marks is not None:
                query += " AND marks <= %s"
                params.append(max_marks)

            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            results.extend(rows)
        except Error as e:
            print(f"⚠ Error searching {node}:", e)
        finally:
            conn.close()
    return results


# ------------------ Initialization Helpers ------------------

def setup_databases():
    """Utility: create 'students' table on all nodes if not exists."""
    schema = """
    CREATE TABLE IF NOT EXISTS students (
        roll_no INT PRIMARY KEY,
        name VARCHAR(100),
        branch VARCHAR(20),
        marks FLOAT,
        attendance FLOAT
    );
    """
    for branch in META["nodes"]:
        conn = connect_to_node(branch)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            cur.execute(schema)
            conn.commit()
            print(f"✅ Table ensured in {branch}")
        except Error as e:
            print(f"❌ Setup failed in {branch}:", e)
        finally:
            conn.close()


if __name__ == "__main__":
    print("🔧 Setting up distributed student databases...")
    setup_databases()
    print("✅ All nodes ready.")
