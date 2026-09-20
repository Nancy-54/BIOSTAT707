from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CHECKPOINT 1
# PhysioNet / Computing in Cardiology Challenge 2012 Set A
#
# Required outputs:
#   1. Table 1: Cohort characteristics
#   2. Outcome summary
#   3. Missingness summary
#   4. Missingness map
#
# Table 1:
#   Continuous variables -> mean (SD)
#   Categorical variables -> n (%)
#   Missing values -> separate row
#
# Groups:
#   Overall
#   In-hospital survival
#   In-hospital death
# ============================================================


# ============================================================
# 1. FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SET_A_DIR = BASE_DIR / "set-a"
OUTCOME_FILE = BASE_DIR / "Outcomes-a.txt"


# ============================================================
# 2. READ OUTCOME DATA
# ============================================================

outcomes = pd.read_csv(
    OUTCOME_FILE
)

print("\n==========================================")
print("OUTCOME DATA")
print("==========================================")

print(
    "Shape:",
    outcomes.shape
)

print(
    outcomes.head()
)


# ============================================================
# 3. READ ALL SET-A PATIENT FILES
# ============================================================

all_records = []

txt_files = sorted(
    SET_A_DIR.glob("*.txt")
)

print(
    "\nNumber of patient files:",
    len(txt_files)
)


for file in txt_files:

    df = pd.read_csv(
        file
    )

    # Find RecordID
    record_rows = df.loc[
        df["Parameter"] == "RecordID",
        "Value"
    ]

    if len(record_rows) == 0:

        print(
            "No RecordID found:",
            file.name
        )

        continue

    record_id = int(
        record_rows.iloc[0]
    )

    df["RecordID"] = record_id

    all_records.append(
        df
    )


# Combine all patient files
long_df = pd.concat(
    all_records,
    ignore_index=True
)


print("\n==========================================")
print("SET-A DATA")
print("==========================================")

print(
    "Number of patients:",
    long_df[
        "RecordID"
    ].nunique()
)

print(
    "Number of parameters:",
    long_df[
        "Parameter"
    ].nunique()
)


# ============================================================
# 4. CONVERT VALUE TO NUMERIC
# ============================================================

long_df["Value"] = pd.to_numeric(
    long_df["Value"],
    errors="coerce"
)


# ============================================================
# 5. REMOVE RECORD ID FROM CLINICAL VARIABLES
# ============================================================

clinical_df = long_df[
    long_df["Parameter"] != "RecordID"
].copy()


# ============================================================
# 6. CREATE STATIC / ADMISSION DATASET
#
# Variables used for Table 1:
#   Age
#   Gender
#   Height
#   Weight
#   ICUType
# ============================================================

static_vars = [
    "Age",
    "Gender",
    "Height",
    "Weight",
    "ICUType"
]


static_df = (
    clinical_df[
        clinical_df[
            "Parameter"
        ].isin(
            static_vars
        )
    ]
    .pivot_table(
        index="RecordID",
        columns="Parameter",
        values="Value",
        aggfunc="first"
    )
    .reset_index()
)


# ============================================================
# 7. HANDLE MISSING VALUES FOR STATIC VARIABLES
#
# -1 = missing / unknown
# ============================================================

for var in static_vars:

    if var in static_df.columns:

        static_df[var] = (
            static_df[var]
            .replace(
                -1,
                np.nan
            )
        )


# ============================================================
# 8. MERGE STATIC DATA WITH OUTCOME DATA
# ============================================================

patient_static = static_df.merge(
    outcomes,
    on="RecordID",
    how="left"
)


N = len(
    patient_static
)


print("\n==========================================")
print("MERGED COHORT")
print("==========================================")

print(
    "Total N:",
    N
)

print(
    "Missing mortality outcomes:",
    patient_static[
        "In-hospital_death"
    ].isna().sum()
)


# ============================================================
# 9. DEFINE TABLE 1 GROUPS
#
# In-hospital survival:
#   In-hospital_death = 0
#
# In-hospital death:
#   In-hospital_death = 1
# ============================================================

overall_df = patient_static


survival_df = patient_static[
    patient_static[
        "In-hospital_death"
    ] == 0
]


death_df = patient_static[
    patient_static[
        "In-hospital_death"
    ] == 1
]


# ============================================================
# 10. TABLE 1 HELPER FUNCTIONS
# ============================================================

table1_rows = []


# ------------------------------------------------------------
# Continuous variable:
# mean (SD)
# ------------------------------------------------------------

def continuous_summary(
    df,
    variable
):

    x = df[
        variable
    ].dropna()

    if len(x) == 0:

        return "NA"

    mean = x.mean()

    sd = x.std()

    return (
        f"{mean:.1f} "
        f"({sd:.1f})"
    )


# ------------------------------------------------------------
# Missing:
# n (%)
# ------------------------------------------------------------

def missing_summary_cell(
    df,
    variable
):

    n_missing = (
        df[
            variable
        ]
        .isna()
        .sum()
    )

    pct_missing = (
        n_missing
        / len(df)
        * 100
    )

    return (
        f"{n_missing} "
        f"({pct_missing:.1f}%)"
    )


# ------------------------------------------------------------
# Add continuous variable
# ------------------------------------------------------------

def add_continuous_variable(
    variable,
    label
):

    # Mean (SD)
    table1_rows.append({

        "Characteristic":
            f"{label}, mean (SD)",

        "Overall":
            continuous_summary(
                overall_df,
                variable
            ),

        "In-hospital survival":
            continuous_summary(
                survival_df,
                variable
            ),

        "In-hospital death":
            continuous_summary(
                death_df,
                variable
            )
    })


    # Missing
    table1_rows.append({

        "Characteristic":
            "    Missing, n (%)",

        "Overall":
            missing_summary_cell(
                overall_df,
                variable
            ),

        "In-hospital survival":
            missing_summary_cell(
                survival_df,
                variable
            ),

        "In-hospital death":
            missing_summary_cell(
                death_df,
                variable
            )
    })


# ------------------------------------------------------------
# Categorical variable:
# n (%)
# ------------------------------------------------------------

def category_summary(
    df,
    variable,
    value
):

    n = (
        df[
            variable
        ] == value
    ).sum()

    pct = (
        n
        / len(df)
        * 100
    )

    return (
        f"{n} "
        f"({pct:.1f}%)"
    )


# ------------------------------------------------------------
# Add categorical variable
# ------------------------------------------------------------

def add_categorical_variable(
    variable,
    label,
    category_labels
):

    # Variable heading
    table1_rows.append({

        "Characteristic":
            f"{label}, n (%)",

        "Overall":
            "",

        "In-hospital survival":
            "",

        "In-hospital death":
            ""
    })


    # Each category
    for value, category_name in (
        category_labels.items()
    ):

        table1_rows.append({

            "Characteristic":
                f"    {category_name}",

            "Overall":
                category_summary(
                    overall_df,
                    variable,
                    value
                ),

            "In-hospital survival":
                category_summary(
                    survival_df,
                    variable,
                    value
                ),

            "In-hospital death":
                category_summary(
                    death_df,
                    variable,
                    value
                )
        })


    # Missing
    table1_rows.append({

        "Characteristic":
            "    Missing",

        "Overall":
            missing_summary_cell(
                overall_df,
                variable
            ),

        "In-hospital survival":
            missing_summary_cell(
                survival_df,
                variable
            ),

        "In-hospital death":
            missing_summary_cell(
                death_df,
                variable
            )
    })


# ============================================================
# 11. BUILD TABLE 1
# ============================================================

# Sample size
table1_rows.append({

    "Characteristic":
        "N",

    "Overall":
        str(
            len(overall_df)
        ),

    "In-hospital survival":
        str(
            len(survival_df)
        ),

    "In-hospital death":
        str(
            len(death_df)
        )
})


# Age
add_continuous_variable(
    "Age",
    "Age, years"
)


# Gender
# 0 = Female
# 1 = Male
add_categorical_variable(

    "Gender",

    "Gender",

    {
        0: "Female",
        1: "Male"
    }
)


# Height
add_continuous_variable(
    "Height",
    "Height, cm"
)


# Weight
add_continuous_variable(
    "Weight",
    "Weight, kg"
)


# ICU Type
# 1 = Coronary Care Unit
# 2 = Cardiac Surgery Recovery Unit
# 3 = Medical ICU
# 4 = Surgical ICU

add_categorical_variable(

    "ICUType",

    "ICU type",

    {
        1:
            "Coronary Care Unit",

        2:
            "Cardiac Surgery Recovery Unit",

        3:
            "Medical ICU",

        4:
            "Surgical ICU"
    }
)


# ============================================================
# 12. CREATE AND DISPLAY TABLE 1
# ============================================================

table1 = pd.DataFrame(
    table1_rows
)


print("\n")
print("==========================================")
print("TABLE 1. COHORT CHARACTERISTICS")
print("==========================================")

print(
    table1.to_string(
        index=False
    )
)


# ============================================================
# 13. EXPORT TABLE 1
# ============================================================

table1.to_csv(
    "Table1.csv",
    index=False
)

print(
    "\nTable1.csv saved."
)


# ============================================================
# 14. CREATE OUTCOME SUMMARY
#
# Outcome-related variables:
#   SAPS-I
#   SOFA
#   Length of stay
#   In-hospital death
#   Survival time
# ============================================================

outcome_rows = []

N_outcome = len(
    outcomes
)


# ------------------------------------------------------------
# Helper function:
# Continuous outcome / descriptor
# ------------------------------------------------------------

def add_continuous_outcome(
    variable,
    label
):

    # -1 = missing / unknown
    x = outcomes[
        variable
    ].replace(
        -1,
        np.nan
    )

    n_nonmissing = (
        x.notna().sum()
    )

    n_missing = (
        x.isna().sum()
    )

    missing_pct = (
        n_missing
        / N_outcome
        * 100
    )

    mean = x.mean()

    sd = x.std()

    median = x.median()

    q1 = x.quantile(
        0.25
    )

    q3 = x.quantile(
        0.75
    )

    minimum = x.min()

    maximum = x.max()


    outcome_rows.append({

        "Outcome":
            label,

        "N":
            int(
                n_nonmissing
            ),

        "Missing n (%)":
            f"{n_missing} "
            f"({missing_pct:.1f}%)",

        "Mean (SD)":
            f"{mean:.2f} "
            f"({sd:.2f})",

        "Median (Q1, Q3)":
            f"{median:.2f} "
            f"({q1:.2f}, {q3:.2f})",

        # Use "to" instead of "-" or en dash
        # to prevent Excel from treating the range as a date
        "Min-Max":
            f"{minimum:.0f} to "
            f"{maximum:.0f}"
    })


# SAPS-I
add_continuous_outcome(
    "SAPS-I",
    "SAPS-I"
)


# SOFA
add_continuous_outcome(
    "SOFA",
    "SOFA"
)


# Length of stay
add_continuous_outcome(
    "Length_of_stay",
    "Length of stay, days"
)


# ------------------------------------------------------------
# In-hospital death
#
# 0 = In-hospital survival
# 1 = In-hospital death
# ------------------------------------------------------------

death_outcome = outcomes[
    "In-hospital_death"
]


n_survival_outcome = (
    death_outcome == 0
).sum()


n_death_outcome = (
    death_outcome == 1
).sum()


n_death_outcome_missing = (
    death_outcome
    .isna()
    .sum()
)


# In-hospital death heading
outcome_rows.append({

    "Outcome":
        "In-hospital death",

    "N":
        "",

    "Missing n (%)":
        (
            f"{n_death_outcome_missing} "
            f"("
            f"{n_death_outcome_missing / N_outcome * 100:.1f}%"
            f")"
        ),

    "Mean (SD)":
        "",

    "Median (Q1, Q3)":
        "",

    "Min-Max":
        ""
})


# In-hospital survival
outcome_rows.append({

    "Outcome":
        "    In-hospital survival",

    "N":
        (
            f"{n_survival_outcome} "
            f"("
            f"{n_survival_outcome / N_outcome * 100:.2f}%"
            f")"
        ),

    "Missing n (%)":
        "",

    "Mean (SD)":
        "",

    "Median (Q1, Q3)":
        "",

    "Min-Max":
        ""
})


# In-hospital death
outcome_rows.append({

    "Outcome":
        "    In-hospital death",

    "N":
        (
            f"{n_death_outcome} "
            f"("
            f"{n_death_outcome / N_outcome * 100:.2f}%"
            f")"
        ),

    "Missing n (%)":
        "",

    "Mean (SD)":
        "",

    "Median (Q1, Q3)":
        "",

    "Min-Max":
        ""
})


# ------------------------------------------------------------
# Survival time
#
# Survival = -1 means no recorded survival time.
#
# -1 is not included when summarizing the distribution
# of recorded survival times.
# ------------------------------------------------------------

survival_raw = outcomes[
    "Survival"
]


no_survival_time = (
    survival_raw == -1
)


recorded_survival_time = (
    survival_raw != -1
) & (
    survival_raw.notna()
)


n_no_survival_time = (
    no_survival_time.sum()
)


n_recorded_survival = (
    recorded_survival_time.sum()
)


survival_valid = (
    survival_raw[
        recorded_survival_time
    ]
)


# Survival time heading
outcome_rows.append({

    "Outcome":
        "Survival time",

    "N":
        "",

    "Missing n (%)":
        "",

    "Mean (SD)":
        "",

    "Median (Q1, Q3)":
        "",

    "Min-Max":
        ""
})


# No recorded survival time
outcome_rows.append({

    "Outcome":
        "    No recorded survival time (-1)",

    "N":
        (
            f"{n_no_survival_time} "
            f"("
            f"{n_no_survival_time / N_outcome * 100:.2f}%"
            f")"
        ),

    "Missing n (%)":
        "",

    "Mean (SD)":
        "",

    "Median (Q1, Q3)":
        "",

    "Min-Max":
        ""
})


# Recorded survival time
outcome_rows.append({

    "Outcome":
        "    Recorded survival time",

    "N":
        (
            f"{n_recorded_survival} "
            f"("
            f"{n_recorded_survival / N_outcome * 100:.2f}%"
            f")"
        ),

    "Missing n (%)":
        "",

    "Mean (SD)":
        (
            f"{survival_valid.mean():.2f} "
            f"({survival_valid.std():.2f})"
        ),

    "Median (Q1, Q3)":
        (
            f"{survival_valid.median():.2f} "
            f"("
            f"{survival_valid.quantile(0.25):.2f}, "
            f"{survival_valid.quantile(0.75):.2f}"
            f")"
        ),

    # Use "to" so Excel does not convert it to a date
    "Min-Max":
        (
            f"{survival_valid.min():.0f} to "
            f"{survival_valid.max():.0f}"
        )
})


# ============================================================
# 15. CREATE AND DISPLAY OUTCOME SUMMARY
# ============================================================

outcome_summary = pd.DataFrame(
    outcome_rows
)


print("\n")
print("==========================================")
print("OUTCOME SUMMARY")
print("==========================================")

print(
    outcome_summary.to_string(
        index=False
    )
)


# ============================================================
# 16. EXPORT OUTCOME SUMMARY
# ============================================================

outcome_summary.to_csv(
    "Outcome_summary.csv",
    index=False
)

print(
    "\nOutcome_summary.csv saved."
)


# ============================================================
# 17. CREATE MISSINGNESS DATA
#
# Missingness analysis uses all predictor variables from Set A.
#
# Observed:
#   Patient had at least one valid measurement.
#
# Missing:
#   Patient had no valid measurement.
# ============================================================

measurement_df = clinical_df.copy()


# -1 = missing / unknown
measurement_df["Value"] = (
    measurement_df[
        "Value"
    ]
    .replace(
        -1,
        np.nan
    )
)


# True = valid value exists
# False = value is missing
measurement_df[
    "observed"
] = (
    measurement_df[
        "Value"
    ].notna()
)


# ============================================================
# 18. CREATE PATIENT x VARIABLE OBSERVATION MATRIX
# ============================================================

observed_matrix = (
    measurement_df
    .groupby(
        [
            "RecordID",
            "Parameter"
        ]
    )[
        "observed"
    ]
    .any()
    .unstack()
)


# Make sure all 4000 patients are represented
all_patient_ids = (
    long_df[
        "RecordID"
    ]
    .drop_duplicates()
    .sort_values()
)


observed_matrix = (
    observed_matrix
    .reindex(
        all_patient_ids
    )
)


# If a patient-variable combination never appears,
# that variable was not measured.
#
# Force Boolean type before inversion.
observed_matrix = (
    observed_matrix
    .fillna(False)
    .astype(bool)
)


# ============================================================
# 19. CREATE MISSINGNESS MATRIX
#
# 0 = observed
# 1 = missing
# ============================================================

missing_matrix = (
    ~observed_matrix
).astype(int)


# Safety check
print(
    "\nUnique values in missingness matrix:"
)

print(
    np.unique(
        missing_matrix.values
    )
)

# This must return:
# [0 1]


# ============================================================
# 20. DEFINE MISSINGNESS GROUPS
#
# In-hospital survival:
#   In-hospital_death = 0
#
# In-hospital death:
#   In-hospital_death = 1
# ============================================================

outcome_lookup = (
    outcomes[
        [
            "RecordID",
            "In-hospital_death"
        ]
    ]
    .set_index(
        "RecordID"
    )
)


missing_with_outcome = (
    missing_matrix
    .join(
        outcome_lookup,
        how="left"
    )
)


survival_missing = (
    missing_with_outcome[
        missing_with_outcome[
            "In-hospital_death"
        ] == 0
    ]
    .drop(
        columns="In-hospital_death"
    )
)


death_missing = (
    missing_with_outcome[
        missing_with_outcome[
            "In-hospital_death"
        ] == 1
    ]
    .drop(
        columns="In-hospital_death"
    )
)


n_survival = len(
    survival_missing
)


n_death = len(
    death_missing
)


print(
    "\nIn-hospital survival N:",
    n_survival
)

print(
    "In-hospital death N:",
    n_death
)


# ============================================================
# 21. CREATE MISSINGNESS SUMMARY
# ============================================================

missing_rows = []


for variable in missing_matrix.columns:

    # --------------------------------------------------------
    # Overall
    # --------------------------------------------------------

    overall_n = len(
        missing_matrix
    )

    overall_missing_n = int(
        missing_matrix[
            variable
        ].sum()
    )

    overall_observed_n = (
        overall_n
        - overall_missing_n
    )

    overall_missing_pct = (
        overall_missing_n
        / overall_n
        * 100
    )

    overall_observed_pct = (
        overall_observed_n
        / overall_n
        * 100
    )


    # --------------------------------------------------------
    # In-hospital survival
    # --------------------------------------------------------

    survival_missing_n = int(
        survival_missing[
            variable
        ].sum()
    )

    survival_observed_n = (
        n_survival
        - survival_missing_n
    )

    survival_missing_pct = (
        survival_missing_n
        / n_survival
        * 100
    )

    survival_observed_pct = (
        survival_observed_n
        / n_survival
        * 100
    )


    # --------------------------------------------------------
    # In-hospital death
    # --------------------------------------------------------

    death_missing_n = int(
        death_missing[
            variable
        ].sum()
    )

    death_observed_n = (
        n_death
        - death_missing_n
    )

    death_missing_pct = (
        death_missing_n
        / n_death
        * 100
    )

    death_observed_pct = (
        death_observed_n
        / n_death
        * 100
    )


    # --------------------------------------------------------
    # Difference in missingness
    #
    # In-hospital death minus in-hospital survival
    #
    # Positive:
    #   More missing in the in-hospital death group.
    #
    # Negative:
    #   More missing in the in-hospital survival group.
    # --------------------------------------------------------

    difference = (
        death_missing_pct
        - survival_missing_pct
    )


    missing_rows.append({

        "Variable":
            variable,

        "Overall Missing n (%)":
            f"{overall_missing_n} "
            f"({overall_missing_pct:.1f}%)",

        "Overall Observed n (%)":
            f"{overall_observed_n} "
            f"({overall_observed_pct:.1f}%)",

        "In-hospital survival Missing n (%)":
            f"{survival_missing_n} "
            f"({survival_missing_pct:.1f}%)",

        "In-hospital survival Observed n (%)":
            f"{survival_observed_n} "
            f"({survival_observed_pct:.1f}%)",

        "In-hospital death Missing n (%)":
            f"{death_missing_n} "
            f"({death_missing_pct:.1f}%)",

        "In-hospital death Observed n (%)":
            f"{death_observed_n} "
            f"({death_observed_pct:.1f}%)",

        "Difference in missingness (pp)":
            round(
                difference,
                1
            )
    })


# ============================================================
# 22. CREATE AND EXPORT MISSINGNESS SUMMARY
# ============================================================

missing_summary = pd.DataFrame(
    missing_rows
)


# Sort by absolute difference between
# in-hospital death and in-hospital survival.
missing_summary[
    "_absolute_difference"
] = (
    missing_summary[
        "Difference in missingness (pp)"
    ].abs()
)


missing_summary = (
    missing_summary
    .sort_values(
        "_absolute_difference",
        ascending=False
    )
    .drop(
        columns="_absolute_difference"
    )
    .reset_index(
        drop=True
    )
)


print("\n")
print("==========================================")
print("MISSINGNESS SUMMARY")
print("==========================================")

print(
    missing_summary.to_string(
        index=False
    )
)


missing_summary.to_csv(
    "Missingness_summary.csv",
    index=False
)


print(
    "\nMissingness_summary.csv saved."
)


# ============================================================
# 23. CREATE MISSINGNESS MAP
# ============================================================

# Order variables from least missing to most missing
missing_percent_for_plot = (
    missing_matrix
    .mean(
        axis=0
    )
    * 100
)


variable_order = (
    missing_percent_for_plot
    .sort_values()
    .index
    .tolist()
)


missing_matrix_plot = (
    missing_matrix[
        variable_order
    ]
)


# Sort patients by total amount of missingness
patient_order = (
    missing_matrix_plot
    .sum(
        axis=1
    )
    .sort_values()
    .index
)


missing_matrix_plot = (
    missing_matrix_plot
    .loc[
        patient_order
    ]
)


plt.figure(
    figsize=(
        15,
        9
    )
)


plt.imshow(
    missing_matrix_plot,
    aspect="auto",
    interpolation="nearest"
)


plt.xlabel(
    "Variables"
)


plt.ylabel(
    "Patients"
)


plt.title(
    "Missingness Map: Challenge 2012 Set A"
)


plt.xticks(
    range(
        len(variable_order)
    ),
    variable_order,
    rotation=90
)


plt.colorbar(
    label="Missing = 1, Observed = 0"
)


plt.tight_layout()


# ============================================================
# 24. SAVE MISSINGNESS MAP AND DISPLAY FINAL OUTPUTS
# ============================================================

plt.savefig(
    "Missingness_map.png",
    dpi=300,
    bbox_inches="tight"
)


plt.show()


print(
    "\nMissingness_map.png saved."
)


print("\n")
print("==========================================")
print("CHECKPOINT 1 OUTPUTS")
print("==========================================")

print(
    "1. Table1.csv"
)

print(
    "2. Outcome_summary.csv"
)

print(
    "3. Missingness_summary.csv"
)

print(
    "4. Missingness_map.png"
)