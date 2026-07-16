from pathlib import Path
import random

import pandas as pd

# Aynı kod her çalıştığında benzer sonuçlar üretmesi için
random.seed(42)

NUMBER_OF_USERS = 500

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "users.csv"


def generate_users(number_of_users: int) -> pd.DataFrame:
    """Generate synthetic user data for the fictional FocusFlow app."""

    countries = ["Turkey", "Germany", "United Kingdom", "Netherlands", "France"]
    acquisition_channels = [
        "Organic Search",
        "Paid Social",
        "App Store",
        "Referral",
        "Influencer",
    ]
    device_types = ["iOS", "Android"]
    genders = ["Female", "Male"]
    subscription_plans = ["Free", "Premium"]

    signup_dates = pd.date_range(
        start="2026-01-01",
        end="2026-03-31",
        periods=number_of_users,
    )

    users = []

    for index in range(number_of_users):
        user = {
            "user_id": f"USR{index + 1:04d}",
            "signup_date": signup_dates[index].date(),
            "age": random.randint(18, 60),
            "gender": random.choice(genders),
            "country": random.choice(countries),
            "acquisition_channel": random.choice(acquisition_channels),
            "device_type": random.choice(device_types),
            "subscription_plan": random.choices(
                subscription_plans,
                weights=[82, 18],
                k=1,
            )[0],
            "marketing_opt_in": random.random() < 0.70,
            "is_active": random.random() < 0.90,
        }

        users.append(user)

    return pd.DataFrame(users)


def main() -> None:
    """Generate users and save them as a CSV file."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    users_df = generate_users(NUMBER_OF_USERS)
    users_df.to_csv(OUTPUT_FILE, index=False)

    print(f"{len(users_df)} users generated successfully.")
    print(f"File saved to: {OUTPUT_FILE}")
    print()
    print(users_df.head())


if __name__ == "__main__":
    main()
