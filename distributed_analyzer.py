import mysql.connector

# connections to both fragments
db_nodes = {
    "CSE": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_cse"},
    "AIML": {"host": "localhost", "user": "root", "password": "@Admin123", "database": "db_aiml"}
}

# gather data from all nodes
all_students = []
for name, cfg in db_nodes.items():
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    all_students.extend(cur.fetchall())
    conn.close()

# --- Algorithmic layer: quicksort by total marks ---
def quicksort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    pivot = key(arr[len(arr)//2])
    left = [x for x in arr if key(x) > pivot]   # descending
    mid  = [x for x in arr if key(x) == pivot]
    right= [x for x in arr if key(x) < pivot]
    return quicksort(left, key) + mid + quicksort(right, key)

# assume marks are in columns 3 and 4; compute total
sorted_students = quicksort(all_students, key=lambda s: s[3] + s[4])

print("\nSorted Students (by total marks):")
for s in sorted_students:
    total = s[3] + s[4]
    print(f"{s[1]} ({s[2]}) -> Total: {total}")
