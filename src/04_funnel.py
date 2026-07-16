import matplotlib.pyplot as plt
import pandas as pd

from utils.data_loader import load_events
from utils.paths import OUTPUT_DIR


OUTPUT_FILE = OUTPUT_DIR / "funnel_chart.png"

FUNNEL_STEPS = [
    ("signup", "Signed Up"),
    ("login", "Logged In"),
    ("start_session", "Started Session"),
    ("complete_session", "Completed Session"),
    ("upgrade_to_premium", "Upgraded to Premium"),
]


def calculate_funnel(events_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate unique users and conversion rates for funnel steps."""

    funnel_rows = []

    for event_name, step_label in FUNNEL_STEPS:
        unique_users = events_df.loc[
            events_df["event_name"] == event_name,
            "user_id",
        ].nunique()

        funnel_rows.append(
            {
                "event_name": event_name,
                "funnel_step": step_label,
                "unique_users": unique_users,
            }
        )

    funnel_df = pd.DataFrame(funnel_rows)

    first_step_users = funnel_df.loc[0, "unique_users"]

    funnel_df["overall_conversion_rate"] = (
        funnel_df["unique_users"] / first_step_users * 100
    )

    funnel_df["step_conversion_rate"] = (
        funnel_df["unique_users"]
        / funnel_df["unique_users"].shift(1)
        * 100
    )

    funnel_df.loc[0, "step_conversion_rate"] = 100.0

    return funnel_df


def create_funnel_chart(funnel_df: pd.DataFrame) -> None:
    """Create and save the funnel chart."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chart_df = funnel_df.iloc[::-1].copy()
    max_users = funnel_df["unique_users"].max()

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        chart_df["funnel_step"],
        chart_df["unique_users"],
    )

    for bar, (_, row) in zip(bars, chart_df.iterrows()):
        width = bar.get_width()

        label = (
            f"{int(row['unique_users'])} users"
            f" | {row['overall_conversion_rate']:.1f}% overall"
        )

        ax.text(
            width + max_users * 0.015,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            fontsize=10,
        )

    ax.set_title(
        "FocusFlow User Conversion Funnel",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.set_xlabel("Unique Users")
    ax.set_ylabel("Funnel Step")
    ax.grid(axis="x", alpha=0.25)

    ax.set_xlim(
        0,
        max_users * 1.38,
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def print_funnel_insights(funnel_df: pd.DataFrame) -> None:
    """Print funnel conversion and drop-off insights."""

    print("FUNNEL RESULTS")
    print("-" * 70)

    for index, row in funnel_df.iterrows():
        print(
            f"{row['funnel_step']}: "
            f"{int(row['unique_users'])} users | "
            f"{row['overall_conversion_rate']:.1f}% overall conversion | "
            f"{row['step_conversion_rate']:.1f}% step conversion"
        )

        if index > 0:
            previous_users = funnel_df.loc[
                index - 1,
                "unique_users",
            ]

            dropped_users = (
                previous_users - row["unique_users"]
            )

            drop_off_rate = (
                dropped_users / previous_users * 100
                if previous_users > 0
                else 0
            )

            print(
                "  Drop-off from previous step: "
                f"{int(dropped_users)} users "
                f"({drop_off_rate:.1f}%)"
            )

    weakest_index = (
        funnel_df.loc[1:, "step_conversion_rate"].idxmin()
    )

    weakest_step = funnel_df.loc[weakest_index]

    print()
    print(
        "Largest conversion problem: "
        f"{weakest_step['funnel_step']} "
        f"with {weakest_step['step_conversion_rate']:.1f}% "
        "conversion from the previous step."
    )


def main() -> None:
    """Run the funnel analysis."""

    events_df = load_events()
    funnel_df = calculate_funnel(events_df)

    create_funnel_chart(funnel_df)

    print("Funnel analysis completed successfully.")
    print(f"Chart saved to: {OUTPUT_FILE}")
    print()

    print_funnel_insights(funnel_df)


if __name__ == "__main__":
    main()