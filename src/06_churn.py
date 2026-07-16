import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "churn_chart.png"


def calculate_subscription_churn(events_df: pd.DataFrame) -> dict:
    premium_users = events_df.loc[
        events_df["event_name"] == "upgrade_to_premium",
        "user_id",
    ].nunique()

    cancelled_users = events_df.loc[
        events_df["event_name"] == "cancel_subscription",
        "user_id",
    ].nunique()

    churn_rate = (
        cancelled_users / premium_users * 100
        if premium_users > 0
        else 0
    )

    return {
        "premium_users": premium_users,
        "cancelled_users": cancelled_users,
        "active_premium_users": premium_users - cancelled_users,
        "churn_rate": churn_rate,
    }
    pass


def create_churn_chart(churn_metrics: dict) -> None:

    premium_users = churn_metrics["premium_users"]
    cancelled_users = churn_metrics["cancelled_users"]
    
    pass


def main() -> None:
    events_df = load_events()

    churn_metrics = calculate_subscription_churn(events_df)

    print(churn_metrics)


if __name__ == "__main__":
    main()