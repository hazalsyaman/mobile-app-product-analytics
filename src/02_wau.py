import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "wau_chart.png"

ACTIVITY_EVENTS = [
    "login",
    "start_session",
    "complete_session",
]


def calculate_wau(events_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate unique active users for each complete calendar week."""

    active_events = events_df[
        events_df["event_name"].isin(ACTIVITY_EVENTS)
    ].copy()

    active_events["week_start"] = (
        active_events["event_timestamp"]
        .dt.to_period("W-SUN")
        .apply(lambda period: period.start_time)
    )

    wau_df = (
        active_events
        .groupby("week_start")["user_id"]
        .nunique()
        .reset_index(name="weekly_active_users")
        .sort_values("week_start")
    )

    # Remove the first and final incomplete weeks.
    first_week_start = wau_df["week_start"].min()
    last_week_start = wau_df["week_start"].max()

    wau_df = wau_df[
        (wau_df["week_start"] > first_week_start)
        & (wau_df["week_start"] < last_week_start)
    ].copy()

    return wau_df


def create_wau_chart(wau_df: pd.DataFrame) -> None:
    """Create and save the WAU chart."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    average_wau = wau_df["weekly_active_users"].mean()

    peak_index = wau_df["weekly_active_users"].idxmax()
    peak_date = wau_df.loc[peak_index, "week_start"]
    peak_value = wau_df.loc[peak_index, "weekly_active_users"]

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(
        wau_df["week_start"],
        wau_df["weekly_active_users"],
        marker="o",
        linewidth=2.2,
        label="Weekly Active Users",
    )

    ax.axhline(
        average_wau,
        linestyle="--",
        linewidth=1.5,
        alpha=0.8,
        label=f"Average WAU: {average_wau:.1f}",
    )

    ax.scatter(
        peak_date,
        peak_value,
        s=80,
        zorder=5,
    )

    ax.annotate(
        f"Peak: {int(peak_value)}",
        xy=(peak_date, peak_value),
        xytext=(-55, 18),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        ha="center",
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 1,
        },
    )

    ax.set_title(
        "FocusFlow Weekly Active Users",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.set_xlabel("Week Starting")
    ax.set_ylabel("Unique Active Users")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", frameon=True)

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
    """Run the WAU analysis."""

    events_df = load_events()
    wau_df = calculate_wau(events_df)

    create_wau_chart(wau_df)

    print("WAU analysis completed successfully.")
    print(f"Chart saved to: {OUTPUT_FILE}")
    print()
    print(wau_df.head())
    print()
    print("WAU summary:")
    print(wau_df["weekly_active_users"].describe())


if __name__ == "__main__":
    main()