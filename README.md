# TCS-Net

## Patient-Specific Temporal Cross-Antibiotic Susceptibility Modeling

TCS-Net is a CBIO313 Data Mining & Machine Learning project that investigates
whether previous antibiotic susceptibility results from the same patient can
help predict resistance in a later recurrent E. coli urine culture.

The main prediction target is Ciprofloxacin resistance. Ampicillin was also
used as a second target to test whether the same modeling approach could
generalize to another antibiotic.

## Project idea

A previous AST result can contain useful information about a later culture,
but the value of this information may change with time.

The model uses:

- Previous susceptibility of the target antibiotic
- Previous susceptibility to other antibiotics
- Time between consecutive cultures
- Interactions between susceptibility results and time

For example, the model can learn a pattern based on:

Previous Ciprofloxacin status + Ceftriaxone status + time interval.

## Data

Two microbiology datasets were used.

### Stanford ARMD

Dryad DOI: `10.5061/dryad.jq2bvq8kp`

The main cohort included:

- Positive urine cultures
- E. coli
- Directly measured AST results
- Susceptible and Resistant results only
- Patients with at least two cultures
- Conflicting AST results removed
- Consecutive cultures more than 14 days apart

After preprocessing, 20,368 valid consecutive culture transitions were
available.

### UTSW ARMD

UT Southwestern data was used for independent external validation.

Dryad DOI: `10.5061/dryad.0rxwdbsd5`

The same main preprocessing rules were applied.

After preprocessing, 11,801 valid consecutive culture transitions were
available.

Stanford-trained models were applied directly to UTSW without site-specific
retraining in the main external validation.

## Time intervals

Time between cultures was divided into:

- 15-90 days
- 91-180 days
- 181-365 days
- 366-730 days
- More than 730 days

## Models

The project includes:

- Logistic Regression
- Decision Tree
- Random Forest

The final analysis compares three feature designs.

### B2

Previous same-drug susceptibility and time.

### D2

B2 features plus previous susceptibility results from other antibiotics.

### TCS-Net

D2 features plus explicit temporal cross-antibiotic interaction terms.

## Main results

### Ciprofloxacin - Stanford temporal validation

| Model | ROC-AUC | PR-AUC | Brier Score |
|---|---:|---:|---:|
| B2 | 0.8235 | 0.7462 | 0.1070 |
| D2 | 0.8262 | 0.7556 | 0.1067 |
| TCS-Net | **0.8737** | **0.7840** | **0.1017** |

TCS-Net improved ROC-AUC by 0.0501 compared with B2.

### Ampicillin - Stanford temporal validation

| Model | ROC-AUC | PR-AUC | Brier Score |
|---|---:|---:|---:|
| B2 | 0.7720 | 0.7681 | 0.1804 |
| D2 | 0.7733 | 0.7784 | 0.1792 |
| TCS-Net | **0.8230** | **0.8048** | **0.1680** |

The same interaction design was used without Ampicillin-specific
hyperparameter tuning.

## External validation

### Ciprofloxacin - UTSW

| Model | ROC-AUC | PR-AUC | Brier Score |
|---|---:|---:|---:|
| B2 | 0.8263 | 0.7696 | 0.1354 |
| D2 | 0.8292 | 0.7841 | 0.1350 |
| TCS-Net | **0.8566** | **0.8001** | **0.1305** |

### Ampicillin - UTSW

| Model | ROC-AUC | PR-AUC | Brier Score |
|---|---:|---:|---:|
| B2 | 0.7613 | 0.7859 | 0.1931 |
| D2 | 0.7623 | 0.7958 | 0.1925 |
| TCS-Net | **0.7974** | **0.8152** | **0.1825** |

The interaction model remained better than the simpler baselines on both
external targets.

## Temporal pattern

Previous Ciprofloxacin susceptibility showed a strong relationship with the
later result, and this relationship changed with time.

For patients with a previous Resistant Ciprofloxacin result:

- 15-90 days: about 92% later resistance
- More than 730 days: about 47% later resistance

These results describe predictive associations only. They do not prove that
the same bacterial strain persisted or that the relationship is causal.

## Smart-AST

The Ciprofloxacin model includes an abstention layer.

Using calibrated resistance probability:

- Probability <= 0.10: Likely Susceptible
- Probability between 0.10 and 0.80: Laboratory AST Required
- Probability >= 0.80: Likely Resistant

Stanford 2022-2023:

- Coverage: 61.1%
- Selective accuracy: 92.0%

UTSW external validation:

- Coverage: 52.5%
- Selective accuracy: 90.0%

The thresholds are research operating points and are not clinical cutoffs.

## Explainability

SHAP and model coefficients were used to examine the contribution of
previous susceptibility results, time, and interaction features.

The explanations describe model behavior and should not be interpreted as
causal biological effects.

## Streamlit demo

The project includes an interactive Streamlit application.

The user enters the previous AST profile and time since the previous culture.
The application returns:

- Raw probability of Ciprofloxacin resistance
- Calibrated probability of resistance
- Smart-AST decision

To run the application:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Repository structure

```text
TCS-Net/
├── app.py
├── README.md
├── requirements.txt
├── data/
├── figures/
├── models/
├── notebooks/
├── presentation/
├── report/
├── results/
└── src/
```

Raw microbiology datasets are not included in the repository because of
their size. Data source information is available in `data/README.md`.

## Limitations

- Same species does not necessarily mean the same bacterial strain.
- The analysis is observational and does not establish causality.
- AST missingness may not be random.
- Laboratory practices may differ between institutions and over time.
- Recurrent-culture patients are a selected patient population.
- Calibration may shift between institutions.
- Smart-AST thresholds are not clinical treatment thresholds.

## Note

This project is for research and educational purposes. It is not intended
to prescribe antibiotics or replace laboratory AST.

## Course

CBIO313 - Data Mining & Machine Learning
