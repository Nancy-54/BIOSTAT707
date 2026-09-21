# Checkpoint 1

## 1. Data Wrangling and Cohort Construction

The Challenge 2012 Set A data consist of 4,000 separate patient-level
files in a skinny format. I combined these files into a single long-format
dataset, `output/set-a_long.csv`, while retaining RecordID, measurement
time, variable name, and measurement value. This preserves the temporal
structure of the measurements during the first 48 hours of the ICU stay.

I also constructed `output/set-a_wide.csv`, with one row per ICU admission.
For this checkpoint, I summarized each repeatedly measured variable over
the full 48-hour prediction window using the number of measurements,
first value, last value, minimum, maximum, and mean. I chose a single
48-hour summary rather than separate 0–24 and 24–48 hour summaries to
create a simple admission-level representation for the initial exploratory
analysis. This decision may be revisited during model development if
changes over time appear to contain useful predictive information. The
outcome data from `data/Outcomes-a.txt` were merged into this admission-level
wide table.


## 2. Table 1: Cohort Characteristics

The analytic cohort included 4,000 ICU patients. Of these, 3,446
(86.15%) survived hospitalization and 554 (13.85%) died in the hospital.

The mean age of the cohort was 64.2 years (SD 17.6). Patients who died
in the hospital were older on average than those who survived
hospitalization (70.0 vs. 63.3 years). Overall, 43.8% of patients were
female and 56.1% were male. The most common ICU type was the Medical ICU
(37.0%), followed by the Surgical ICU (26.7%), Cardiac Surgery Recovery
Unit (21.9%), and Coronary Care Unit (14.4%).

Height was missing at admission for 47.3% of patients, while admission
weight was missing for 8.2%. This distinction is important because the
Table 1 summaries describe admission/static information, whereas the
48-hour missingness analysis asks whether a variable was observed at
least once during the full prediction window.


## 3. Outcome Summary

In-hospital mortality was 13.85% (554/4,000). SAPS-I was available for
3,810 patients, with a mean of 14.96 (SD 5.18) and median of 15
(Q1 11, Q3 19). SOFA was available for 3,856 patients, with a mean of
6.68 (SD 4.02) and median of 7 (Q1 3, Q3 9). Length of stay was available
for 3,940 patients, with a mean of 13.66 days (SD 12.21) and median of
10 days (Q1 6, Q3 17).

For the Survival variable, 2,526 patients (63.15%) had no recorded
survival time (-1), while 1,474 (36.85%) had a recorded survival time.
Among patients with a recorded survival time, the median was 70 days
(Q1 10.25, Q3 479), with a range from 0 to 2,600 days.


## 4. Exploratory Analysis of Measurement Values

I examined the distributions of measurements in `set-a_long.csv` using
the number of observations, minimum, first quartile, median, third
quartile, and maximum for each variable. The results are saved in
`output/measurement_range_summary.csv`.

This inspection identified several values that warrant additional
attention. For example, temperature ranged from -17.8 to 42.1, pH ranged
from 1 to 735, height ranged from 1.8 to 431.8 cm, heart rate included
values of 0 and reached 300, and potassium reached 22.9. Some of these
extreme values are physiologically implausible or may reflect recording,
unit, or data-entry problems rather than true clinical measurements.
Other variables also contain clinically extreme values that cannot be
classified as errors based only on their magnitude.

For this checkpoint, I did not automatically delete observations solely
because they were extreme. I treated the documented missing-value code
(-1) as missing and used the range summary to flag questionable
measurements for review. Before using these variables in a predictive
model, I would compare questionable values with the variable definitions
and clinically justified ranges and then apply explicit, reproducible
cleaning rules. This avoids silently removing true but unusually severe
clinical measurements.


## 5. Missingness in the 48-Hour Data

Missingness varied substantially across variables. Several routinely
measured variables had little or no patient-level missingness over the
48-hour window, including Age (0.0%), ICUType (0.0%), Gender (0.1%),
HR (1.6%), BUN (1.6%), Creatinine (1.6%), HCT (1.6%), Temp (1.6%),
GCS (1.6%), and Platelets (1.7%).

In contrast, some measurements were absent for a large proportion of
patients. TroponinI had the highest patient-level missingness (94.9%),
followed by Cholesterol (92.4%), TroponinT (78.4%), RespRate (72.5%),
Albumin (59.6%), ALP (57.8%), Bilirubin (57.0%), ALT (57.0%), AST
(56.9%), and SaO2 (55.2%). Lactate was missing for 45.4% of patients.

Missingness also differed by in-hospital death status. For example,
lactate was missing for 47.8% of patients who survived hospitalization
but only 30.5% of patients who died, a difference of approximately
-17.3 percentage points. AST showed a similar pattern (59.5% missing
among survivors versus 40.6% among patients who died). In contrast,
RespRate was more often missing among patients who died (84.3%) than
among survivors (70.6%).

These patterns suggest that missingness is plausibly informative rather
than simply random noise. In an ICU setting, whether a test is ordered
can reflect the patient's clinical condition and clinicians' assessment
of which measurements are necessary. For example, a patient with no
lactate measurement is not equivalent to a patient whose lactate was
measured and found to be normal. The differences by mortality status
are consistent with an informative measurement process. However, these
descriptive results do not establish a specific missing-data mechanism
or show that missingness itself causes the outcome.


## 6. Temporal Missingness

Because `set-a_long.csv` retains measurement time, I also examined
missingness over the 48-hour observation window rather than considering
only whether a variable was ever measured. I divided the 48-hour window
into eight 6-hour intervals and, for each time-varying clinical variable,
calculated the percentage of admissions with no valid measurement in
each interval. The results are shown in
`output/Temporal_missingness.png` and summarized in
`output/Temporal_missingness.csv`.

The temporal analysis shows that measurement frequency is not constant
over the ICU stay. Frequently monitored variables such as heart rate,
temperature, GCS, and urine output remain relatively well observed
throughout the 48-hour period. In contrast, laboratory measurements are
generally less frequent and many become less commonly observed in later
intervals. Lactate, for example, was absent for 65.5% of admissions
during hours 0–6 and for 90.8% during hours 42–48. Troponin and
cholesterol measurements were sparse throughout the observation window.

This temporal structure provides information that is lost when the
entire 48-hour period is reduced to a single missing/not-missing
indicator. It also suggests that both whether a measurement was obtained
and when it was obtained may contain information about clinical care and
patient status.


## 7. Information Available at Prediction Time

Prediction-time information is restricted to information available
during the first 48 hours of the ICU stay. This includes admission/general
descriptors (Age, Gender, Height, ICUType, and Weight) and time-series
clinical measurements recorded during the 48-hour observation window.

For repeatedly measured variables, only measurements obtained within
these first 48 hours are available. The number and timing of measurements,
as well as the fact that a variable was not measured during part or all
of this window, are also observable at prediction time and may themselves
contain useful information.

Information occurring after the first 48 hours must not be used as a
predictor. In particular, the final in-hospital death outcome, total
length of stay, and later survival information are unavailable at
prediction time and therefore should not be used as predictor variables.
These outcome-related variables are summarized in this checkpoint only
for cohort characterization.


## 8. Challenge 2012 Assessment Criteria

The eventual predictive model will be evaluated using the Challenge 2012
assessment criteria, including the minimum of sensitivity and positive
predictive value, min(TP/(TP+FN), TP/(TP+FP)), as well as the
Hosmer-Lemeshow statistic for calibration. At this checkpoint I have not
fit a prediction model, so these criteria are not calculated. Their role
at this stage is to clarify that later model evaluation will need to
consider both classification performance and calibration rather than
only overall accuracy.


## 9. Use of AI Tools

I used ChatGPT as an AI-assisted programming and learning tool during
this checkpoint. I used it primarily to help interpret the assignment
requirements, troubleshoot Python and Git/Pixi workflow issues, and
debug code.

A major benefit of AI assistance was that it helped me identify coding
and workflow issues more quickly. There were also important limitations. 
AI-generated code or explanations were not assumed to be correct. Suggestions 
sometimes needed to be modified to match the exact assignment requirements, 
repository structure, variable definitions, or properties of the Challenge 
2012 data.