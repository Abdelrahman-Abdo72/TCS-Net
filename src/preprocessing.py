import pandas as pd


def filter_ecoli_urine_ast(df, time_col):
    """Return positive E. coli urine cultures with binary AST results."""
    data = df[
        (df["was_positive"] == 1)
        & (df["culture_description"] == "URINE")
        & (df["organism"] == "ESCHERICHIA COLI")
        & (df["susceptibility"].isin(["Susceptible", "Resistant"]))
    ].copy()

    data[time_col] = pd.to_datetime(
        data[time_col],
        errors="coerce"
    )

    return data


def remove_conflicting_ast(df):
    """Remove culture-antibiotic combinations containing both S and R."""
    keys = [
        "anon_id",
        "order_proc_id_coded",
        "antibiotic"
    ]

    audit = (
        df.groupby(keys)["susceptibility"]
        .nunique()
        .reset_index(name="n_status")
    )

    conflicts = audit[audit["n_status"] > 1][keys]

    clean = df.merge(
        conflicts.assign(is_conflict=1),
        on=keys,
        how="left"
    )

    clean = clean[
        clean["is_conflict"].isna()
    ].drop(columns="is_conflict")

    clean = clean.drop_duplicates(
        subset=keys,
        keep="first"
    )

    return clean


def recurrent_patients(df, minimum_cultures=2):
    """Keep patients with at least the requested number of cultures."""
    counts = (
        df.groupby("anon_id")["order_proc_id_coded"]
        .nunique()
    )

    patient_ids = counts[
        counts >= minimum_cultures
    ].index

    return df[
        df["anon_id"].isin(patient_ids)
    ].copy()
