from pathlib import Path

DATA_DIR = Path("DATA")

def migrate_users(conn):
    path = DATA_DIR / "users.txt"
    if not path.exists():
        print("users.txt not found, skipping user migration")
        return

    cur = conn.cursor()
    migrated = 0

    with open(path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        line = f.readline().strip() if first.lower().startswith("username") else first

        while line:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                username, password_hash = parts[:2]
                role = parts[2] if len(parts) >= 3 else "user"

                cur.execute("""
                    INSERT OR IGNORE INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                """, (username, password_hash, role))

                if cur.rowcount > 0:
                    migrated += 1

            line = f.readline().strip()

    conn.commit()
    print(f"Users migrated: {migrated}")
