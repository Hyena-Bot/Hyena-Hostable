import sqlite3

QUERIES = {
    "action-logs": """
    CREATE TABLE "moderation_actions" (
        "user_id"	INTEGER,
        "actions"	TEXT,
        PRIMARY KEY("user_id")
    );
    """,
    "warns": """
    CREATE TABLE "warns" (
        "user_id"	INTEGER,
        "warn_data"	TEXT,
        PRIMARY KEY("user_id")
    );
    """,
}

for x, y in QUERIES.items():
    db = sqlite3.connect(x + ".sqlite")
    cursor = db.cursor()
    try:
        cursor.execute(y)
    except sqlite3.OperationalError as exc:
        print("ignoring", exc)
        continue
    db.commit()
    cursor.close()
    db.close()

print("All databases created successfully!")
