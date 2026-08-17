
import streamlit as st
import pandas as pd
import numpy as np
import pickle


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="TCS-Net Smart-AST",
    page_icon="🧬",
    layout="wide"
)


# ==========================================
# CLEAN PRESENTATION UI
# ==========================================

st.markdown(
    """
    <style>

    /* Hide Streamlit toolbar / menu */
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Hide Streamlit footer */
    footer {
        visibility: hidden !important;
    }

    /* Hide top decoration */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Reduce unnecessary top spacing */
    .block-container {
        padding-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# LOAD MODEL
# ==========================================

@st.cache_resource
def load_bundle():

    with open(
        "tcsnet_app_bundle.pkl",
        "rb"
    ) as f:

        return pickle.load(f)


bundle = load_bundle()

model = bundle["model"]
platt = bundle["platt_calibrator"]

FEATURES = bundle["features"]

LOW_THRESHOLD = bundle["low_threshold"]
HIGH_THRESHOLD = bundle["high_threshold"]

cross_antibiotics = bundle[
    "cross_antibiotics"
]


# ==========================================
# FUNCTIONS
# ==========================================

def apply_platt_calibration(
    raw_probability
):

    eps = 1e-6

    p = np.clip(
        raw_probability,
        eps,
        1 - eps
    )

    logit = np.log(
        p / (1 - p)
    )

    calibrated = (
        platt.predict_proba(
            np.array([[logit]])
        )[0, 1]
    )

    return calibrated


def create_interactions(
    row
):

    previous_cipro = row[
        "Ciprofloxacin"
    ]

    time_window = row[
        "time_window_str"
    ]

    for drug in cross_antibiotics:

        drug_status = row[drug]

        row[
            f"INT_{drug}"
        ] = (
            f"{previous_cipro}"
            f"__{drug_status}"
            f"__{time_window}"
        )

    return row


def smart_ast_decision(
    probability
):

    if probability <= LOW_THRESHOLD:

        return (
            "Likely Susceptible",
            "High-confidence susceptible-region prediction"
        )

    elif probability >= HIGH_THRESHOLD:

        return (
            "Likely Resistant",
            "High-confidence resistant-region prediction"
        )

    else:

        return (
            "Laboratory AST Required",
            "Prediction lies in the abstention region"
        )


# ==========================================
# HEADER
# ==========================================

st.title(
    "🧬 TCS-Net: Temporal Cross-Antibiotic Susceptibility Network"
)

st.markdown(
    """
    **Research demonstration of patient-specific temporal
    cross-antibiotic susceptibility prediction.**

    TCS-Net estimates the probability that a **future/recurrent
    E. coli urine isolate will be resistant to Ciprofloxacin**
    using the patient's previous AST profile and time between cultures.
    """
)

st.warning(
    "Research demo only — not a clinical recommendation, "
    "not a replacement for laboratory AST, and not validated "
    "for treatment selection."
)


# ==========================================
# USER INPUT
# ==========================================


st.header(
    "1. Previous Patient AST Profile"
)

status_options = [
    "Susceptible",
    "Resistant",
    "Missing"
]


col1, col2, col3 = st.columns(3)


with col1:

    previous_cipro = st.selectbox(
        "Previous Ciprofloxacin",
        status_options,
        index=0
    )

    ampicillin = st.selectbox(
        "Previous Ampicillin",
        status_options,
        index=0
    )


with col2:

    tmpsmx = st.selectbox(
        "Previous TMP-SMX",
        status_options,
        index=0
    )

    gentamicin = st.selectbox(
        "Previous Gentamicin",
        status_options,
        index=0
    )


with col3:

    cefazolin = st.selectbox(
        "Previous Cefazolin",
        status_options,
        index=0
    )

    ceftriaxone = st.selectbox(
        "Previous Ceftriaxone",
        status_options,
        index=0
    )


st.header(
    "2. Time Since Previous Culture"
)

time_window = st.selectbox(
    "Time interval",
    bundle["time_windows"],
    index=0
)


# ==========================================
# PREDICTION
# ==========================================

st.divider()

if st.button(
    "Run TCS-Net Prediction",
    type="primary",
    use_container_width=True
):

    input_row = {
        "Ciprofloxacin":
            previous_cipro,

        "time_window_str":
            time_window,

        "Ampicillin":
            ampicillin,

        "Trimethoprim/Sulfamethoxazole":
            tmpsmx,

        "Gentamicin":
            gentamicin,

        "Cefazolin":
            cefazolin,

        "Ceftriaxone":
            ceftriaxone
    }


    # --------------------------------------
    # Create locked interaction features
    # --------------------------------------

    input_row = create_interactions(
        input_row
    )

    input_df = pd.DataFrame([
        input_row
    ])

    input_df = input_df[
        FEATURES
    ]


    # --------------------------------------
    # Raw Stanford model probability
    # --------------------------------------

    raw_probability = (
        model.predict_proba(
            input_df
        )[0, 1]
    )


    # --------------------------------------
    # Stanford Platt calibration
    # --------------------------------------

    calibrated_probability = (
        apply_platt_calibration(
            raw_probability
        )
    )


    decision, explanation = (
        smart_ast_decision(
            calibrated_probability
        )
    )


    # ======================================
    # RESULTS
    # ======================================

    st.header(
        "3. Prediction Result"
    )

    metric1, metric2, metric3 = (
        st.columns(3)
    )


    with metric1:

        st.metric(
            "Raw P(Resistance)",
            f"{raw_probability:.1%}"
        )


    with metric2:

        st.metric(
            "Calibrated P(Resistance)",
            f"{calibrated_probability:.1%}"
        )


    with metric3:

        st.metric(
            "Smart-AST Decision",
            decision
        )


    # --------------------------------------
    # Visual probability
    # --------------------------------------

    st.progress(
        float(
            calibrated_probability
        )
    )


    # --------------------------------------
    # Decision explanation
    # --------------------------------------

    if decision == "Likely Susceptible":

        st.success(
            "Smart-AST result: "
            "**Likely Susceptible**"
        )

    elif decision == "Likely Resistant":

        st.error(
            "Smart-AST result: "
            "**Likely Resistant**"
        )

    else:

        st.warning(
            "Smart-AST abstains: "
            "**Laboratory AST Required**"
        )


    st.caption(
        explanation
    )


    # ======================================
    # THRESHOLD EXPLANATION
    # ======================================

    st.subheader(
        "Smart-AST Safety Layer"
    )

    threshold_table = pd.DataFrame({
        "Probability Region": [
            f"≤ {LOW_THRESHOLD:.2f}",
            (
                f"{LOW_THRESHOLD:.2f} "
                f"to {HIGH_THRESHOLD:.2f}"
            ),
            f"≥ {HIGH_THRESHOLD:.2f}"
        ],

        "System Action": [
            "Likely Susceptible",
            "Laboratory AST Required",
            "Likely Resistant"
        ]
    })

    st.dataframe(
        threshold_table,
        use_container_width=True,
        hide_index=True
    )


    # ======================================
    # INPUT SUMMARY
    # ======================================

    with st.expander(
        "View model input"
    ):

        display_input = pd.DataFrame({
            "Variable": [
                "Previous Ciprofloxacin",
                "Previous Ampicillin",
                "Previous TMP-SMX",
                "Previous Gentamicin",
                "Previous Cefazolin",
                "Previous Ceftriaxone",
                "Time interval"
            ],

            "Value": [
                previous_cipro,
                ampicillin,
                tmpsmx,
                gentamicin,
                cefazolin,
                ceftriaxone,
                time_window
            ]
        })

        st.dataframe(
            display_input,
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "TCS-Net models patient-level temporal "
    "cross-antibiotic susceptibility associations. "
    "Same species does not imply the same bacterial lineage, "
    "and predictions should not be interpreted causally."
)
