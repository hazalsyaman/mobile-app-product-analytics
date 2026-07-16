import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "dau_chart.png"

ACTIVITY_EVENTS = [
    "login",
    "start_session",
    "complete_session",
]


def calculate_dau(events_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate unique active users for each day."""

    active_events = events_df[
        events_df["event_name"].isin(ACTIVITY_EVENTS)
    ].copy()

    active_events["activity_date"] = (
        active_events["event_timestamp"].dt.normalize()
    )

    dau_df = (
        active_events
        .groupby("activity_date")["user_id"]
        .nunique()
        .reset_index(name="daily_active_users")
        .sort_values("activity_date")
    )

    # Remove the final incomplete day.
    last_activity_date = dau_df["activity_date"].max()

    dau_df = dau_df[
        dau_df["activity_date"] < last_activity_date
    ].copy()

    dau_df["rolling_7_day_average"] = (
        dau_df["daily_active_users"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    return dau_df


def create_dau_chart(dau_df: pd.DataFrame) -> None:
    """Create and save the DAU chart."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    average_dau = dau_df["daily_active_users"].mean()

    peak_index = dau_df["daily_active_users"].idxmax()
    peak_date = dau_df.loc[peak_index, "activity_date"]
    peak_value = dau_df.loc[peak_index, "daily_active_users"]

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(
        dau_df["activity_date"],
        dau_df["daily_active_users"],
        linewidth=1.5,
        alpha=0.55,
        label="Daily Active Users",
    )

    ax.plot(
        dau_df["activity_date"],
        dau_df["rolling_7_day_average"],
        linewidth=2.5,
        label="7-Day Moving Average",
    )

    ax.axhline(
        average_dau,
        linestyle="--",
        linewidth=1.5,
        alpha=0.8,
        label=f"Average DAU: {average_dau:.1f}",
    )

    ax.scatter(
        peak_date,
        peak_value,
        s=70,
        zorder=5,
    )

    ax.annotate(
        f"Peak: {int(peak_value)}",
        xy=(peak_date, peak_value),
        xytext=(10, 12),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
    )

    ax.set_title(
        "FocusFlow Daily Active Users",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Unique Active Users")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", frameon=True)

    ax.set_ylim(
        bottom=0,
        top=peak_value * 1.12,
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def main() -> None:
    """Run the DAU analysis."""

    events_df = load_events()
    dau_df = calculate_dau(events_df)

    create_dau_chart(dau_df)

    print("DAU analysis completed successfully.")
    print(f"Chart saved to: {OUTPUT_FILE}")
    print()
    print(dau_df.head())
    print()
    print("DAU summary:")
    print(dau_df["daily_active_users"].describe())


if __name__ == "__main__":
    main()