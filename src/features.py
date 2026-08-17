import numpy as np


TIME_WINDOWS = [
    "15-90 days",
    "91-180 days",
    "181-365 days",
    "366-730 days",
    ">730 days"
]


def add_time_window(df, days_col="days_to_next_culture"):
    """Convert time between cultures into the five TCS-Net windows."""
    data = df.copy()
    days = data[days_col]

    data["time_window_str"] = np.select(
        [
            (days > 14) & (days <= 90),
            (days > 90) & (days <= 180),
            (days > 180) & (days <= 365),
            (days > 365) & (days <= 730),
            days > 730
        ],
        TIME_WINDOWS,
        default="Missing"
    )

    return data


def add_temporal_interactions(
    df,
    target_drug,
    cross_antibiotics,
    time_col="time_window_str"
):
    """Create target x cross-antibiotic x time interaction features."""
    data = df.copy()

    target_status = (
        data[target_drug]
        .astype("string")
        .fillna("Missing")
    )

    time_status = (
        data[time_col]
        .astype("string")
        .fillna("Missing")
    )

    for drug in cross_antibiotics:
        cross_status = (
            data[drug]
            .astype("string")
            .fillna("Missing")
        )

        data[f"INT_{drug}"] = (
            target_status
            + "__"
            + cross_status
            + "__"
            + time_status
        )

    return data
