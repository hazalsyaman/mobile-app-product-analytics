from pathlib import Path
from datetime import timedelta
import random

import pandas as pd


random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
USERS_FILE = PROJECT_ROOT / "data" / "users.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "events.csv"

ANALYSIS_END_DATE = pd.Timestamp("2026-04-30 23:59:59")


def load_users() -> pd.DataFrame:
    """Load synthetic users and prepare column types."""

    if not USERS_FILE.exists():
        raise FileNotFoundError(
            "users.csv was not found. Run generate_users.py first."
        )

    users_df = pd.read_csv(USERS_FILE)
    users_df["signup_date"] = pd.to_datetime(
        users_df["signup_date"]
    )

    return users_df


def create_event(
    user: pd.Series,
    event_name: str,
    event_timestamp: pd.Timestamp,
) -> dict:
    """Create a single event record."""

    return {
        "user_id": user["user_id"],
        "event_name": event_name,
        "event_timestamp": event_timestamp,
        "platform": user["device_type"],
        "country": user["country"],
    }


def calculate_daily_return_probability(
    days_since_signup: int,
    is_active: bool,
) -> float:
    """Return a realistic probability of activity for a given day."""

    if days_since_signup == 0:
        return 0.88 if is_active else 0.55

    if days_since_signup <= 3:
        return 0.65 if is_active else 0.25

    if days_since_signup <= 7:
        return 0.48 if is_active else 0.16

    if days_since_signup <= 14:
        return 0.34 if is_active else 0.10

    if days_since_signup <= 30:
        return 0.24 if is_active else 0.06

    if days_since_signup <= 60:
        return 0.17 if is_active else 0.03

    return 0.12 if is_active else 0.015


def generate_daily_activity(
    user: pd.Series,
    activity_date: pd.Timestamp,
) -> list[dict]:
    """Generate login and focus-session activity for one active day."""

    daily_events = []

    login_count = random.choices(
        population=[1, 2, 3],
        weights=[75, 20, 5],
        k=1,
    )[0]

    for _ in range(login_count):
        login_timestamp = activity_date + pd.Timedelta(
            hours=random.randint(7, 22),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        daily_events.append(
            create_event(
                user=user,
                event_name="login",
                event_timestamp=login_timestamp,
            )
        )

        # Not every login leads to a focus session.
        if random.random() < 0.74:
            start_timestamp = login_timestamp + pd.Timedelta(
                minutes=random.randint(1, 12)
            )

            daily_events.append(
                create_event(
                    user=user,
                    event_name="start_session",
                    event_timestamp=start_timestamp,
                )
            )

            # Not every started session is completed.
            if random.random() < 0.70:
                complete_timestamp = start_timestamp + pd.Timedelta(
                    minutes=random.randint(15, 60)
                )

                daily_events.append(
                    create_event(
                        user=user,
                        event_name="complete_session",
                        event_timestamp=complete_timestamp,
                    )
                )

    return daily_events


def generate_subscription_events(
    user: pd.Series,
    signup_timestamp: pd.Timestamp,
) -> list[dict]:
    """Generate premium upgrade and possible cancellation events."""

    subscription_events = []

    if user["subscription_plan"] != "Premium":
        return subscription_events

    upgrade_timestamp = signup_timestamp + pd.Timedelta(
        days=random.randint(1, 21),
        hours=random.randint(1, 12),
    )

    if upgrade_timestamp > ANALYSIS_END_DATE:
        return subscription_events

    subscription_events.append(
        create_event(
            user=user,
            event_name="upgrade_to_premium",
            event_timestamp=upgrade_timestamp,
        )
    )

    # A proportion of premium users cancel later.
    if random.random() < 0.18:
        cancel_timestamp = upgrade_timestamp + pd.Timedelta(
            days=random.randint(14, 45),
            hours=random.randint(1, 12),
        )

        if cancel_timestamp <= ANALYSIS_END_DATE:
            subscription_events.append(
                create_event(
                    user=user,
                    event_name="cancel_subscription",
                    event_timestamp=cancel_timestamp,
                )
            )

    return subscription_events


def generate_events(users_df: pd.DataFrame) -> pd.DataFrame:
    """Generate realistic user behavior over time."""

    events = []

    for _, user in users_df.iterrows():
        signup_timestamp = user["signup_date"] + pd.Timedelta(
            hours=random.randint(7, 22),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        user_events = [
            create_event(
                user=user,
                event_name="signup",
                event_timestamp=signup_timestamp,
            )
        ]

        is_active = bool(user["is_active"])

        final_activity_date = ANALYSIS_END_DATE.normalize()

        current_date = signup_timestamp.normalize()

        while current_date <= final_activity_date:
            days_since_signup = (
                current_date - signup_timestamp.normalize()
            ).days

            return_probability = (
                calculate_daily_return_probability(
                    days_since_signup=days_since_signup,
                    is_active=is_active,
                )
            )

            if random.random() < return_probability:
                user_events.extend(
                    generate_daily_activity(
                        user=user,
                        activity_date=current_date,
                    )
                )

            current_date += pd.Timedelta(days=1)

        user_events.extend(
            generate_subscription_events(
                user=user,
                signup_timestamp=signup_timestamp,
            )
        )

        events.extend(user_events)

    events.sort(
        key=lambda event: (
            event["event_timestamp"],
            event["user_id"],
        )
    )

    for event_number, event in enumerate(events, start=1):
        event["event_id"] = f"EVT{event_number:06d}"

    events_df = pd.DataFrame(events)

    return events_df[
        [
            "event_id",
            "user_id",
            "event_name",
            "event_timestamp",
            "platform",
            "country",
        ]
    ]


def save_events(events_df: pd.DataFrame) -> None:
    """Save the generated events to a CSV file."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    events_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )


def main() -> None:
    """Run the complete event-generation process."""

    users_df = load_users()
    events_df = generate_events(users_df)

    save_events(events_df)

    print(
        f"{len(events_df)} events generated successfully."
    )
    print(f"File saved to: {OUTPUT_FILE}")
    print()

    print("Event distribution:")
    print(events_df["event_name"].value_counts())
    print()

    active_dates = (
        events_df[
            events_df["event_name"].isin(
                [
                    "login",
                    "start_session",
                    "complete_session",
                ]
            )
        ]
        .assign(
            activity_date=lambda dataframe:
            pd.to_datetime(
                dataframe["event_timestamp"]
            ).dt.date
        )
        .groupby("user_id")["activity_date"]
        .nunique()
    )

    print("Active-day summary per user:")
    print(active_dates.describe())


if __name__ == "__main__":
    main()