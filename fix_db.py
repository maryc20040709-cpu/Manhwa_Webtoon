with open("app/database.py", "r") as f:
    content = f.read()

old = "def get_history(limit: int = 10):\n    conn = sqlite3.connect(DB_PATH)"
new = "def get_history(limit: int = 10):\n    init_db()  # ensure table exists\n    conn = sqlite3.connect(DB_PATH)"
content = content.replace(old, new, 1)

with open("app/database.py", "w") as f:
    f.write(content)

print("Done!")
