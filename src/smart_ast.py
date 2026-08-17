import numpy as np


def apply_platt_calibration(probabilities, calibrator):
    """Apply a fitted Platt model to raw probabilities."""
    probabilities = np.asarray(probabilities)

    clipped = np.clip(
        probabilities,
        1e-6,
        1 - 1e-6
    )

    logits = np.log(
        clipped / (1 - clipped)
    ).reshape(-1, 1)

    return calibrator.predict_proba(logits)[:, 1]


def smart_ast_decision(
    probability,
    low_threshold=0.10,
    high_threshold=0.80
):
    """Return the research Smart-AST decision."""
    if probability <= low_threshold:
        return "Likely Susceptible"

    if probability >= high_threshold:
        return "Likely Resistant"

    return "Laboratory AST Required"
