import mysql.connector

db_nodes = {
    "CSE": {
        "host": "localhost",
        "user": "root",
        "password": "@Admin123",
        "database": "db_cse"
    },
    "AIML": {
        "host": "localhost",
        "user": "root",
        "password": "@Admin123",
        "database": "db_aiml"
    }
}

for name, config in db_nodes.items():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students;")
    rows = cursor.fetchall()
    print(f"\nData from {name} node:")
    for r in rows:
        print(r)
    conn.close()
