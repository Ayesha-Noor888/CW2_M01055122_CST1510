from pathlib import Path
import sqlite3

DATA_DIR = Path("DATA")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "intelligence_platform.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))
