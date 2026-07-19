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


def create_churn_chart(churn_metrics: dict) -> None:

    active_premium_users = churn_metrics["active_premium_users"]
    cancelled_users = churn_metrics["cancelled_users"]

    labels = ["Active Premium", "Cancelled"]
    values = [active_premium_users, cancelled_users]

    plt.figure(figsize=(6, 4)),
    plt.title("Subscription Churn Analysis")
    plt.xlabel("Number of Users")
    plt.ylabel("User Category")
    plt.xlim(0, max(values) + 10)

    bars = plt.barh(labels, values)

    for bar in bars:
        width = bar.get_width()

    plt.text(
        width+1,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width)}",
        va="center",
        )
    
    plt.figtext(
    0.5,
    0.02,
    f"Churn Rate: {churn_metrics['churn_rate']:.2f}%",
    ha="center",
    fontsize=10,
    )
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    plt.show()


def main() -> None:
    events_df = load_events()

    churn_metrics = calculate_subscription_churn(events_df)

    print("\n========== Subscription Churn Report ==========")
    print(f"Premium Users        : {churn_metrics['premium_users']}")
    print(f"Cancelled Users      : {churn_metrics['cancelled_users']}")
    print(f"Active Premium Users : {churn_metrics['active_premium_users']}")
    print(f"Churn Rate           : {churn_metrics['churn_rate']:.2f}%")

    create_churn_chart(churn_metrics)


if __name__ == "__main__":
    main()