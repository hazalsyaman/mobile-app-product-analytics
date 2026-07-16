import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "mau_chart.png"

ACTIVITY_EVENTS = [
    "login",
    "start_session",
    "complete_session",
]


def calculate_mau(events_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate unique active users for each complete calendar month."""

    active_events = events_df[
        events_df["event_name"].isin(ACTIVITY_EVENTS)
    ].copy()

    active_events["month"] = (
        active_events["event_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    mau_df = (
        active_events
        .groupby("month")["user_id"]
        .nunique()
        .reset_index(name="monthly_active_users")
        .sort_values("month")
    )

    # Remove the final incomplete month.
    last_month = mau_df["month"].max()

    mau_df = mau_df[
        mau_df["month"] < last_month
    ].copy()

    return mau_df


def create_mau_chart(mau_df: pd.DataFrame) -> None:
    """Create and save the MAU chart."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    average_mau = mau_df["monthly_active_users"].mean()
    peak_value = mau_df["monthly_active_users"].max()

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(
        mau_df["month"].dt.strftime("%b %Y"),
        mau_df["monthly_active_users"],
    )

    ax.axhline(
        average_mau,
        linestyle="--",
        linewidth=1.5,
        alpha=0.8,
        label=f"Average MAU: {average_mau:.1f}",
    )

    for bar in bars:
        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 6,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_title(
        "FocusFlow Monthly Active Users",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Unique Active Users")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper left")

    ax.set_ylim(
        bottom=0,
        top=peak_value * 1.15,
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def main() -> None:
    """Run the MAU analysis."""

    events_df = load_events()
    mau_df = calculate_mau(events_df)

    create_mau_chart(mau_df)

    print("MAU analysis completed successfully.")
    print(f"Chart saved to: {OUTPUT_FILE}")
    print()
    print(mau_df)
    print()
    print("MAU summary:")
    print(mau_df["monthly_active_users"].describe())


if __name__ == "__main__":
    main()