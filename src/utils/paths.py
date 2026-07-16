from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

USERS_FILE = DATA_DIR / "users.csv"
EVENTS_FILE = DATA_DIR / "events.csv"