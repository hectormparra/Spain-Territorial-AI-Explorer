# Spain Territorial AI Explorer

**AI for SDG 11 — Sustainable Cities and Communities**  
Samsung Innovation Campus Capstone · Assignment 2 working prototype

## What the tool does

This local Streamlit application lets a user select and compare Spanish municipalities, view an AI estimate of **historical 2015–2025 population growth**, inspect the observed result, and explore 2024–2025 rental and economic indicators. It includes an adjustable rules-based territorial screening table and model evaluation details.

**Important:** This is a *retrospective backtest*, not a forecast of future population. The model uses only pre-2016 population information. Rental and economic indicators are contextual data and do not influence the prediction. Territorial screening is not an AI ranking.

## Quick start

Install Python 3.10+ and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The browser should open the local app, typically at `http://localhost:8501`.

## Demo workflow

1. Open **Municipality AI estimate**, select a municipality and inspect predicted vs observed growth.
2. Inspect the historical population chart and contextual housing/economic indicators.
3. Open **Compare municipalities** and select two municipalities.
4. Open **Territorial screening**, adjust criteria, review matching municipalities, and download a CSV.
5. Open **Model evaluation** and **Methods and ethics**.

## Model and evaluation

- Inputs: log population in 2015; population growth 1996–2015, 2005–2010, 2005–2015 and 2010–2015.
- Target: percent population growth from 2015 to 2025.
- Random Forest: 150 trees, min_samples_leaf=8, max_features=0.8, random_state=42.
- Random split: 80% training, 20% test; 8,117 municipalities with valid target, 1,624 held out.
- Test metrics: Random Forest MAE 8.70 percentage points, RMSE 12.95 pp, R² 0.334; Ridge MAE 9.46 pp, RMSE 13.89 pp, R² 0.234.
- Final deployable model refitted on all valid historical rows *after* testing. Do not interpret per-municipality displayed errors as held-out errors.

## Data and provenance

`data/municipalities.csv` is a compact derived dataset based on the integrated project spreadsheet combining:

- INE, municipal population series 1996–2025: https://www.ine.es/jaxiT3/files/t/xlsx/29005.xlsx
- MIVAU Urban Areas Atlas: https://atlasau.mivau.gob.es/
- MIVAU SERPAVI: https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi

Not all indicators cover all municipalities. Missing data remain missing. Municipal codes are five-character strings and should not be converted to integers.

## Repository layout

```
app.py
requirements.txt
models/population_growth_rf.joblib
data/municipalities.csv
data/validation_metrics.csv
reports/Assignment_2_Results_Report_EN.pdf
slides/Assignment_2_Presentation_EN.pptx
DEMO_VIDEO_SCRIPT_EN.md
README.md
```

## Ethics and limitations

The model does not infer causality, model future mobility, or measure the actual quality of public services. Errors and missing data may vary by region and municipality size. Users should not use outputs as stand-alone investment or public-policy recommendations. Further evaluation should test later periods and geographic transfer, add historically aligned economic/transport indicators, and involve intended users.

## Submission checklist

- [ ] Create a GitHub repository and upload these files (no credentials or private information).
- [ ] Add the public GitHub repository URL to the submission.
- [ ] Record a 2–3 minute screen demo following `DEMO_VIDEO_SCRIPT_EN.md`.
- [ ] Verify whether the teacher also requires the separate one-page report and presentation in Homework 2.
- [ ] Insert the group members and follow the required filename convention.
