import pandas as pd

from utils.paths import EVENTS_FILE, USERS_FILE


def load_users() -> pd.DataFrame:
    """Load the users dataset and prepare its data types."""

    if not USERS_FILE.exists():
        raise FileNotFoundError(
            "users.csv was not found. Run generate_users.py first."
        )

    users_df = pd.read_csv(USERS_FILE)

    users_df["signup_date"] = pd.to_datetime(
        users_df["signup_date"]
    )

    return users_df


def load_events() -> pd.DataFrame:
    """Load the events dataset and prepare its data types."""

    if not EVENTS_FILE.exists():
        raise FileNotFoundError(
            "events.csv was not found. Run generate_events.py first."
        )

    events_df = pd.read_csv(EVENTS_FILE)

    events_df["event_timestamp"] = pd.to_datetime(
        events_df["event_timestamp"]
    )

    return events_df