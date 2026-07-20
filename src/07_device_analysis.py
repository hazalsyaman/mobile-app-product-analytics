import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events, load_users
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "device_conversion_chart.png"


def calculate_device_conversion(
    users_df: pd.DataFrame,
    events_df: pd.DataFrame,
) -> pd.Series:
    """
    Calculate premium conversion rate by device type.
    """

    merged_df = users_df.merge(events_df, on="user_id")

    premium_df = merged_df.loc[
        merged_df["event_name"] == "upgrade_to_premium"
    ]

    premium_counts = premium_df["device_type"].value_counts()

    device_counts = users_df["device_type"].value_counts()

    conversion_rate = (
        premium_counts
        / device_counts
        * 100
    )

    return conversion_rate.sort_values(ascending=False)


def create_device_chart(conversion_rate: pd.Series) -> None:
    """
    Create device conversion rate chart.
    """

    labels = conversion_rate.index
    values = conversion_rate.values

    plt.figure(figsize=(6, 4))

    bars = plt.bar(labels, values)

    plt.title("Premium Conversion Rate by Device")
    plt.xlabel("Device Type")
    plt.ylabel("Conversion Rate (%)")

    plt.ylim(0, max(values) + 5)

    for bar in bars:
        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.3,
            f"{height:.2f}%",
            ha="center",
        )

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    plt.show()


def print_report(conversion_rate: pd.Series) -> None:
    """
    Print terminal report.
    """

    print("\n========== Device Conversion Report ==========\n")

    for device, rate in conversion_rate.items():
        print(f"{device:<10}: {rate:.2f}%")

    best_device = conversion_rate.idxmax()

    print("\n---------------------------------------------")
    print(f"Best Performing Device : {best_device}")
    print("---------------------------------------------")


def main() -> None:

    users_df = load_users()
    events_df = load_events()

    conversion_rate = calculate_device_conversion(
        users_df,
        events_df,
    )

    print_report(conversion_rate)

    create_device_chart(conversion_rate)


if __name__ == "__main__":
    main()