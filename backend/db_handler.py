import mysql.connector
from mysql.connector import Error
import json
import os
from typing import List, Optional, Tuple

# ------------------ Config & Metadata ------------------

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "meta_config.json")

DEFAULT_META = {
    "nodes": {
        "CSE": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_cse"},
        "AIML": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_aiml"},
        "DS": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_ds"},
        "CC": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_cc"}
    },
    "replication_enabled": False
}


def load_meta() -> dict:
    """Load distributed metadata configuration, create default if missing."""
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_META, f, indent=4)
        return DEFAULT_META
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    # Backward-compatible migration: if old format without "nodes", adapt it
    if "nodes" not in data and any(k.isupper() and isinstance(v, dict) for k, v in data.items()):
        data = {"nodes": data, "replication_enabled": False}
    return data


META = load_meta()

# ------------------ Connection Utilities ------------------


def connect_to_node(branch: str):
    """Return a mysql.connector connection to the named node, or None on failure."""
    branch_u = branch.upper()
    if branch_u not in META["nodes"]:
        raise ValueError(f"Unknown branch: {branch}")
    config = META["nodes"][branch_u]
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"❌ Connection error ({branch_u}): {e}")
        return None


def get_all_connections() -> dict:
    """Open connections to all available nodes and return dict {branch: conn}."""
    conns = {}
    for branch in META["nodes"]:
        conn = connect_to_node(branch)
        if conn:
            conns[branch] = conn
    return conns


# ------------------ CRUD Operations ------------------


def add_student(roll_no: int, name: str, branch: str, marks: float, attendance: float) -> bool:
    """Insert student into the correct node and optionally replicate."""
    branch_u = branch.upper()
    conn = connect_to_node(branch_u)
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (roll_no, name, branch, marks, attendance) VALUES (%s, %s, %s, %s, %s)",
            (roll_no, name, branch_u, marks, attendance)
        )
        conn.commit()
        # optional replication to other nodes (simple REPLACE strategy)
        if META.get("replication_enabled", False):
            replicate_to_others(roll_no, name, branch_u, marks, attendance)
        return True
    except Error as e:
        # duplicate primary key and other errors are handled gracefully
        print(f"❌ Error adding student ({branch_u}): {e}")
        return False
    finally:
        conn.close()


def replicate_to_others(roll_no: int, name: str, branch: str, marks: float, attendance: float) -> None:
    """Replicate a student record to all nodes except the origin. Uses REPLACE INTO for idempotence."""
    for other in META["nodes"]:
        if other == branch:
            continue
        conn = connect_to_node(other)
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
            print(f"⚠ Replication to {other} failed: {e}")
        finally:
            conn.close()


def update_student(roll_no: int, branch: str, new_marks: float, new_attendance: float) -> bool:
    """Update marks/attendance on the correct node. Returns True if any row updated."""
    branch_u = branch.upper()
    conn = connect_to_node(branch_u)
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
        print(f"❌ Error updating student ({branch_u}): {e}")
        return False
    finally:
        conn.close()


def delete_student(roll_no: int, branch: str) -> bool:
    """Delete a student record from the specified node. Returns True if deleted."""
    branch_u = branch.upper()
    conn = connect_to_node(branch_u)
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE roll_no=%s", (roll_no,))
        conn.commit()
        return cur.rowcount > 0
    except Error as e:
        print(f"❌ Error deleting student ({branch_u}): {e}")
        return False
    finally:
        conn.close()


# ------------------ Distributed Retrieval ------------------


def fetch_all_students() -> List[Tuple]:
    """Fetch all students from every node (simple union)."""
    students = []
    conns = get_all_connections()
    for branch, conn in conns.items():
        try:
            cur = conn.cursor()
            cur.execute("SELECT roll_no, name, branch, marks, attendance FROM students;")
            rows = cur.fetchall()
            students.extend(rows)
        except Error as e:
            print(f"⚠ Error fetching from {branch}: {e}")
        finally:
            conn.close()
    return students


# ------------------ Query Optimization Helpers ------------------


def create_indexes() -> None:
    """
    Create commonly used indexes on each node to speed selection and range queries.
    This is a one-time setup helper you can call manually.
    """
    index_statements = [
        # Note: MySQL doesn't support IF NOT EXISTS for CREATE INDEX prior to 8.0 in the same way,
        # but using simple CREATE INDEX and catching exceptions is fine here.
        "CREATE INDEX idx_branch ON students(branch)",
        "CREATE INDEX idx_marks ON students(marks)",
        "CREATE INDEX idx_roll_no ON students(roll_no)",
        "CREATE INDEX idx_attendance ON students(attendance)"
    ]
    for branch in META["nodes"]:
        conn = connect_to_node(branch)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            for stmt in index_statements:
                try:
                    cur.execute(stmt)
                except Error:
                    # index probably exists; ignore
                    pass
            conn.commit()
            print(f"✅ Indexes ensured on {branch}")
        except Error as e:
            print(f"⚠ Index creation failed on {branch}: {e}")
        finally:
            conn.close()


def get_total_student_count() -> int:
    """Return total number of students across all nodes (helper for percentile computations)."""
    total = 0
    for conn in get_all_connections().values():
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM students;")
            total += cur.fetchone()[0]
        except Error as e:
            print("⚠ Error counting students:", e)
        finally:
            conn.close()
    return total


# ------------------ Advanced Filtering API ------------------


def filter_students(
    branch: Optional[str] = None,
    roll_from: Optional[int] = None,
    roll_to: Optional[int] = None,
    marks_min: Optional[float] = None,
    marks_max: Optional[float] = None,
    attendance_min: Optional[float] = None,
    attendance_max: Optional[float] = None,
    top_percentile: Optional[float] = None
) -> List[Tuple]:
    """
    Optimized multi-criteria filter over distributed nodes.

    Returns list of rows (roll_no, name, branch, marks, attendance).

    The function contains:
      - commented SIMPLE query versions (for teaching),
      - and an OPTIMIZED query builder that pushes predicates into each node.

    Supported filters:
      - branch: only that node (CSE/AIML/DS/CC)
      - roll range: roll_from <= roll_no <= roll_to
      - marks range: marks_min <= marks <= marks_max
      - attendance range: attendance_min <= attendance <= attendance_max
      - top_percentile: return students with marks >= threshold computed from global data

    Implementation notes:
      - Predicate pushdown: WHERE clause built per node and only required columns projected.
      - Uses indexes (call create_indexes() once) for speed.
    """

    # If top_percentile is provided we compute a global marks threshold first (simple approach).
    marks_threshold = None
    if top_percentile is not None:
        # e.g., top_percentile=10 -> top 10% students by marks
        total = get_total_student_count()
        if total == 0:
            return []
        # collect all marks (could be optimized further with distributed ORDER BY + LIMIT)
        all_marks = []
        conns = get_all_connections()
        for _, conn in conns.items():
            try:
                cur = conn.cursor()
                cur.execute("SELECT marks FROM students;")
                all_marks.extend([r[0] for r in cur.fetchall()])
            except Error as e:
                print("⚠ Error fetching marks for percentile calc:", e)
            finally:
                conn.close()
        if not all_marks:
            return []
        # compute threshold mark for top X%
        all_marks.sort(reverse=True)
        cutoff_index = max(0, int((top_percentile / 100.0) * len(all_marks)) - 1)
        marks_threshold = all_marks[cutoff_index]

    # Determine target nodes
    target_nodes = [branch.upper()] if branch else list(META["nodes"].keys())
    results = []

    for node in target_nodes:
        conn = connect_to_node(node)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            # ---------------- Simple (explicit) query version (commented for teaching) ----------------
            # SIMPLE version (less efficient):
            # query = "SELECT * FROM students WHERE 1=1"
            # if branch: query += " AND branch = %s"
            # if roll_from: query += " AND roll_no >= %s"
            # if roll_to: query += " AND roll_no <= %s"
            # if marks_min: query += " AND marks >= %s"
            # if marks_max: query += " AND marks <= %s"
            # if attendance_min: query += " AND attendance >= %s"
            # if attendance_max: query += " AND attendance <= %s"
            # params = [branch, roll_from, roll_to, marks_min, marks_max, attendance_min, attendance_max] (filtered)

            # ---------------- Optimized version (predicate pushdown + projection) ----------------
            projected_cols = "roll_no, name, branch, marks, attendance"
            where_clauses = []
            params = []

            # branch predicate is not necessary if node is the branch, but keep for safety
            if branch:
                where_clauses.append("branch = %s")
                params.append(branch.upper())

            if roll_from is not None:
                where_clauses.append("roll_no >= %s")
                params.append(roll_from)
            if roll_to is not None:
                where_clauses.append("roll_no <= %s")
                params.append(roll_to)
            if marks_min is not None:
                where_clauses.append("marks >= %s")
                params.append(marks_min)
            if marks_max is not None:
                where_clauses.append("marks <= %s")
                params.append(marks_max)
            if attendance_min is not None:
                where_clauses.append("attendance >= %s")
                params.append(attendance_min)
            if attendance_max is not None:
                where_clauses.append("attendance <= %s")
                params.append(attendance_max)
            if marks_threshold is not None:
                where_clauses.append("marks >= %s")
                params.append(marks_threshold)

            where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
            # final optimized query (projection + pushed predicates)
            query = f"SELECT {projected_cols} FROM students{where_sql};"

            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            results.extend(rows)
        except Error as e:
            print(f"⚠ Error filtering on {node}: {e}")
        finally:
            conn.close()

    return results


# ------------------ Backwards-compatible search wrapper ------------------


def search_students(keyword: Optional[str] = None,
                    min_marks: Optional[float] = None,
                    max_marks: Optional[float] = None,
                    branch: Optional[str] = None) -> List[Tuple]:
    """
    Backwards-compatible wrapper used by the GUI. Maps to filter_students.
    Keeps semantics of previous API: keyword -> name LIKE '%keyword%'.
    """
    # Map keyword to name filter; others passed directly
    # Use optimized filter_students under the hood but with name LIKE implemented across nodes
    results = []
    target_nodes = [branch.upper()] if branch else list(META["nodes"].keys())

    for node in target_nodes:
        conn = connect_to_node(node)
        if not conn:
            continue
        try:
            cur = conn.cursor()
            # Simple (commented) query:
            # SELECT * FROM students WHERE name LIKE %keyword% AND marks >= min_marks AND marks <= max_marks;

            # Optimized: project columns and push filters
            query = "SELECT roll_no, name, branch, marks, attendance FROM students WHERE 1=1"
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
            print(f"⚠ Error searching on {node}: {e}")
        finally:
            conn.close()
    return results


# ------------------ Setup / Utility ------------------


def setup_databases() -> None:
    """Create 'students' table on all nodes if it doesn't exist."""
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
            print(f"❌ Setup failed in {branch}: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    print("🔧 Setting up distributed student databases...")
    setup_databases()
    print("ℹ️ Optionally run create_indexes() once to improve filter performance.")
    print("✅ All nodes ready.")
