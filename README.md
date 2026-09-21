# Checkpoint 1

The analysis combines the patient-level Set A files into a long-format dataset, constructs an admission-level wide dataset, summarizes cohort characteristics and outcomes, and explores both patient-level and temporal patterns of missingness during the first 48 hours of the ICU stay.

## Data

The raw data are not included in this repository. Before running the analysis, the following files should be available:

```text
data/
├── Outcomes-a.txt
└── set-a/
    ├── 132539.txt
    ├── ...
    └── [4000 patient files]
```

The analysis does not download or modify the raw data.

## Reproducible Environment

This project uses Pixi to manage the computational environment and dependencies. The environment is specified by `pixi.toml` and locked by `pixi.lock`.

From the repository root, run the complete analysis with:

```bash
pixi run --locked checkpoint1
```

No command-line arguments or additional commands are required.

## Outputs

Running the analysis creates the `output/` directory and generates the derived datasets, summary tables, and figures used in the checkpoint analysis:

```text
output/
├── set-a_long.csv
├── set-a_wide.csv
├── measurement_range_summary.csv
├── Temporal_missingness.csv
├── Temporal_missingness.png
├── Table1.csv
├── Outcome_summary.csv
├── Missingness_summary.csv
└── Missingness_map.png
```

`set-a_long.csv` preserves the time-stamped measurements from the first 48 hours of each ICU stay.

`set-a_wide.csv` contains one row per admission with per-variable summaries over the 48-hour window, including count, first, last, minimum, maximum, and mean values.

See `checkpoint1_writeup.md` for the interpretation of the results and the declaration and assessment of AI use.