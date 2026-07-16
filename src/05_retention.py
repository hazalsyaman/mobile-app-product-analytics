import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.data_loader import load_events, load_users
from utils.paths import OUTPUT_DIR


CHART_FILE = OUTPUT_DIR / "retention_heatmap.png"
TABLE_FILE = OUTPUT_DIR / "weekly_retention_table.csv"

ACTIVITY_EVENTS = [
    "login",
    "start_session",
    "complete_session",
]

MAX_RETENTION_WEEK = 12


def prepare_retention_data(
    users_df: pd.DataFrame,
    events_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """Prepare weekly cohort and activity information."""

    users = users_df.copy()
    events = events_df.copy()

    users["cohort_week"] = (
        users["signup_date"]
        .dt.to_period("W-SUN")
        .apply(lambda period: period.start_time)
    )

    active_events = events[
        events["event_name"].isin(ACTIVITY_EVENTS)
    ].copy()

    active_events["activity_week"] = (
        active_events["event_timestamp"]
        .dt.to_period("W-SUN")
        .apply(lambda period: period.start_time)
    )

    active_events = active_events.merge(
        users[
            [
                "user_id",
                "cohort_week",
            ]
        ],
        on="user_id",
        how="left",
    )

    active_events["retention_week"] = (
        (
            active_events["activity_week"]
            - active_events["cohort_week"]
        ).dt.days
        // 7
    )

    active_events = active_events[
        active_events["retention_week"].between(
            0,
            MAX_RETENTION_WEEK,
        )
    ].copy()

    # The final calendar week may contain only partial data.
    final_event_week = (
        events["event_timestamp"]
        .max()
        .to_period("W-SUN")
        .start_time
    )

    last_complete_week = (
        final_event_week - pd.Timedelta(weeks=1)
    )

    return users, active_events, last_complete_week


def calculate_weekly_retention(
    users_df: pd.DataFrame,
    active_events: pd.DataFrame,
    last_complete_week: pd.Timestamp,
) -> pd.DataFrame:
    """Calculate weekly cohort retention percentages."""

    cohort_sizes = (
        users_df
        .groupby("cohort_week")["user_id"]
        .nunique()
        .rename("cohort_size")
    )

    active_users = (
        active_events
        .groupby(
            [
                "cohort_week",
                "retention_week",
            ]
        )["user_id"]
        .nunique()
        .reset_index(name="active_users")
    )

    retention_counts = active_users.pivot(
        index="cohort_week",
        columns="retention_week",
        values="active_users",
    )

    retention_table = retention_counts.div(
        cohort_sizes,
        axis=0,
    ) * 100

    retention_table = retention_table.reindex(
        columns=range(MAX_RETENTION_WEEK + 1)
    )

    # Week 0 represents the full signup cohort.
    retention_table[0] = 100.0

    # Hide weeks that had not yet occurred for newer cohorts.
    for cohort_week in retention_table.index:
        maximum_observable_week = (
            (
                last_complete_week - cohort_week
            ).days
            // 7
        )

        for week_number in retention_table.columns:
            if week_number > maximum_observable_week:
                retention_table.loc[
                    cohort_week,
                    week_number,
                ] = np.nan

    retention_table = retention_table[
        retention_table.index <= last_complete_week
    ].copy()

    retention_table.index = (
        retention_table.index.strftime("%d %b %Y")
    )

    retention_table.columns = [
        f"Week {week_number}"
        for week_number in retention_table.columns
    ]

    return retention_table


def create_retention_heatmap(
    retention_table: pd.DataFrame,
) -> None:
    """Create and save a weekly cohort retention heatmap."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure_height = max(
        7,
        len(retention_table) * 0.48,
    )

    fig, ax = plt.subplots(
        figsize=(15, figure_height)
    )

    heatmap = ax.imshow(
        retention_table.to_numpy(dtype=float),
        aspect="auto",
        vmin=0,
        vmax=100,
    )

    ax.set_title(
        "FocusFlow Weekly Cohort Retention",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )

    ax.set_xlabel("Weeks Since Signup")
    ax.set_ylabel("Signup Cohort")

    ax.set_xticks(
        range(len(retention_table.columns))
    )
    ax.set_xticklabels(
        retention_table.columns,
        rotation=45,
        ha="right",
    )

    ax.set_yticks(
        range(len(retention_table.index))
    )
    ax.set_yticklabels(
        retention_table.index
    )

    for row_index in range(
        len(retention_table.index)
    ):
        for column_index in range(
            len(retention_table.columns)
        ):
            value = retention_table.iloc[
                row_index,
                column_index,
            ]

            if pd.notna(value):
                ax.text(
                    column_index,
                    row_index,
                    f"{value:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                )

    colorbar = fig.colorbar(
        heatmap,
        ax=ax,
        pad=0.02,
    )

    colorbar.set_label(
        "Retention Rate (%)"
    )

    fig.tight_layout()

    fig.savefig(
        CHART_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def print_retention_insights(
    retention_table: pd.DataFrame,
) -> None:
    """Print average retention rates and cohort insights."""

    print("WEEKLY RETENTION SUMMARY")
    print("-" * 60)

    for column in retention_table.columns[1:]:
        available_values = (
            retention_table[column].dropna()
        )

        if not available_values.empty:
            print(
                f"{column}: "
                f"{available_values.mean():.1f}% "
                "average retention"
            )

    mature_cohorts = retention_table[
        retention_table["Week 4"].notna()
    ]

    if not mature_cohorts.empty:
        best_cohort = (
            mature_cohorts["Week 4"].idxmax()
        )

        best_value = mature_cohorts.loc[
            best_cohort,
            "Week 4",
        ]

        print()
        print(
            "Best Week 4 cohort: "
            f"{best_cohort} "
            f"with {best_value:.1f}% retention"
        )


def main() -> None:
    """Run the weekly cohort retention analysis."""

    users_df = load_users()
    events_df = load_events()

    (
        prepared_users,
        active_events,
        last_complete_week,
    ) = prepare_retention_data(
        users_df=users_df,
        events_df=events_df,
    )

    retention_table = calculate_weekly_retention(
        users_df=prepared_users,
        active_events=active_events,
        last_complete_week=last_complete_week,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    retention_table.to_csv(TABLE_FILE)

    create_retention_heatmap(
        retention_table
    )

    print(
        "Retention analysis completed successfully."
    )
    print(f"Chart saved to: {CHART_FILE}")
    print(f"Table saved to: {TABLE_FILE}")
    print()

    print(retention_table.head())
    print()

    print_retention_insights(
        retention_table
    )


if __name__ == "__main__":
    main()