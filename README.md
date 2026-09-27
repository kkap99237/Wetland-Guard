# ?? Wetland Guard
### An Explainable AI-Powered Early-Warning and Risk-Prioritisation System for Wetland Degradation

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework: Streamlit](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Earth Observation: Copernicus](https://img.shields.io/badge/satellite-Sentinel--2%20%7C%20Sentinel--1-green.svg)](https://copernicus.eu/)
[![Tests: Pytest](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](https://pytest.org/)

---

## ?? Executive Summary

**Wetland Guard** is an explainable artificial intelligence decision-support screening system that monitors multi-sensor satellite time series over real Indian wetlands (focusing on 15 Ramsar and ISRO NWIA priority wetland ecosystems in Tamil Nadu). By fusing **Copernicus Sentinel-2 optical reflectance**, **Copernicus Sentinel-1 C-band synthetic aperture radar (SAR)**, and **JRC historical surface water dynamics**, the system identifies multi-indicator deterioration anomalies, estimates a calibrated degradation risk score (0?100), synthesizes evidence-based human-interpretable reason codes, and ranks wetlands to direct field enforcement and conservation interventions.

> **Decision-Support & Screening Advisory:**
> Wetland Guard is an **early-warning screening tool**. It does not claim definitive prediction of future destruction, nor does it replace ground-truth legal surveys or field ecological assessments. A high risk score indicates statistical resemblance to historical degradation trajectories.

---

## ?? Problem Statement & Positioning

### The Problem
Traditional wetland conservation faces critical operational bottlenecks:
- **Static Inventories:** Conventional atlases tell us *where* wetlands are, but not *which* wetlands are actively deteriorating right now.
- **Single-Indicator Vulnerability:** Relying solely on optical vegetation indices (e.g. NDVI) misinterprets normal dry-season monsoonal senescence as permanent destruction.
- **Lack of Prioritisation:** Forest departments and wetland authorities possess limited field patrol capacity and cannot inspect hundreds of water bodies simultaneously without targeted early-warning screening.

### Novelty & Scientific Positioning
We do **not** claim that nobody has mapped wetlands or that this is the first AI wetland prediction system. 

Our core contribution is an **explainable multi-indicator temporal risk-prioritisation workflow** that combines:
1. Multi-sensor satellite observations (Optical + SAR + Hydrology).
2. Strictly backward-looking temporal feature engineering (rolling windows, trends, baseline z-score anomalies with zero future leakage).
3. Supervised machine-learning risk scoring (Random Forest Classifier evaluated against Logistic Regression).
4. Evidence-based, quantitative reason codes explaining *why* an alert was generated.
5. Priority ranking for field investigation dispatch.

| Dimension | Conventional Wetland Mapping | Change Detection Tools | **Wetland Guard** |
|---|---|---|---|
| **Core Question** | "Where are the wetlands?" | "What changed between two rasters?" | **"Which wetland is deteriorating, why, and which should be visited first?"** |
| **Data Fusion** | Single sensor (optical) | Optical or SAR separately | **Copernicus S2 + S1 SAR + JRC Surface Water + GLDAS** |
| **Temporal Context** | Single date snapshot | Bitemporal difference | **Multi-year monthly time-series baseline z-scores** |
| **Output** | Static boundary polygon | Change pixel map | **0?100 Prioritisation Score + Evidence Reason Codes** |

---

## ??? System Architecture

```mermaid
graph TD
    A[ISRO SAC NWIA / Ramsar Boundaries<br/>Tamil Nadu 15 Priority Wetlands] --> B[Data Ingestion Pipeline]
    B --> C1[Google Earth Engine API<br/>COPERNICUS/S2_SR_HARMONIZED<br/>COPERNICUS/S1_GRD<br/>JRC Global Surface Water]
    B --> C2[Real Satellite Observation Ingestion<br/>data/processed/wetland_observations.csv]
    B --> C3[User CSV Upload Interface]
    C1 --> D[Data Validation & Quality Scoring<br/>0.1 to 1.0 Data Quality Metric]
    C2 --> D
    C3 --> D
    D --> E[Temporal Feature Engineering<br/>Strict Backward Rolling, Trends, Baseline Anomaly]
    E --> F[Retrospective Weak Supervision Target<br/>Multi-Indicator Persistent Decline]
    F --> G[Chronological Split<br/>70% Train / 15% Val / 15% Test]
    G --> H1[Random Forest Classifier<br/>200 Trees, class_weight='balanced']
    G --> H2[Logistic Regression Baseline<br/>StandardScaler, Balanced]
    H1 --> I[Evaluation & Checkpointing<br/>models/ & outputs/]
    I --> J[Risk Scoring 0-100 & Evidence Reasons<br/>Low / Medium / High Priority Ranking]
    J --> K[Streamlit Multi-Page Dashboard<br/>1_Dashboard | 2_Explorer | 3_Prioritization | 4_ML | 5_Sources]
```

---

## ?? Real-World Data Sources

Wetland Guard is designed strictly around real-world data:

1. **ISRO / SAC VEDAS National Wetland Inventory & Assessment (NWIA):**
   - *Source:* Space Applications Centre (SAC), ISRO, Ahmedabad.
   - *URL:* [https://vedas.sac.gov.in/...](https://vedas.sac.gov.in/en/National_Wetland_Inventory_and_Assessment_%28NWIA%29_Atlas.html)
   - *Role:* Ground reference geometries, baseline area (ha), and wetland classification for 15 Tamil Nadu Ramsar & priority sites.
2. **Copernicus Sentinel-2 MSI Surface Reflectance (`COPERNICUS/S2_SR_HARMONIZED`):**
   - *URL:* [Google Earth Engine S2 SR Harmonized](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
   - *Spectral Bands:* Blue (B2), Green (B3), Red (B4), NIR (B8), SWIR1 (B11), SWIR2 (B12), QA60 Cloud Mask.
   - *Indices:* NDVI, MNDWI, EVI, AWEI.
3. **Copernicus Sentinel-1 C-SAR (`COPERNICUS/S1_GRD`):**
   - *URL:* [Google Earth Engine S1 GRD](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD)
   - *Polarizations:* Dual VV and VH backscatter (dB), SAR first difference ($\Delta 	ext{SAR}$), and cross-polarization ratio.
4. **JRC Global Surface Water (`JRC/GSW1_4/GlobalSurfaceWater`):**
   - *URL:* [JRC Global Surface Water](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater)
   - *Metrics:* Historical water occurrence, water recurrence, and inter-annual water spread change.
5. **NASA GLDAS-2.1 / Noah Land Surface Model:**
   - *URL:* [NASA GLDAS Noah](https://developers.google.com/earth-engine/datasets/catalog/NASA_GLDAS_V021_NOAH_G025_T3H)
   - *Metrics:* Shallow and root-zone volumetric soil moisture ($m^3/m^3$).

---

## ?? Study Area: 15 Priority Wetlands of Tamil Nadu

Saved in `data/raw/tamil_nadu_wetlands.geojson`:
1. **Pallikaranai Marsh** (Chennai, Ramsar #2484) ? Urban freshwater marsh under landfill and encroachment pressure.
2. **Point Calimere Wildlife & Bird Sanctuary** (Nagapattinam, Ramsar #1210) ? Coastal lagoon, salt pans, and mangroves.
3. **Pichavaram Mangrove** (Cuddalore, Ramsar #2486) ? Estuarine mangrove forest and tidal channels.
4. **Vedanthangal Bird Sanctuary** (Chengalpattu, Ramsar #2488) ? Historic freshwater irrigation tank and breeding heronry.
5. **Karikili Bird Sanctuary** (Chengalpattu, Ramsar #2487) ? Rainfed irrigation tank ecosystem.
6. **Koonthankulam Bird Sanctuary** (Tirunelveli, Ramsar #2485) ? Southern Tamil Nadu community-protected wetland.
7. **Chitrangudi Bird Sanctuary** (Ramanathapuram, Ramsar #2489) ? Semi-arid drought-vulnerable irrigation tank.
8. **Kanjirankulam Bird Sanctuary** (Ramanathapuram, Ramsar #2490) ? Seasonal wetland in drought-prone district.
9. **Vaduvur Bird Sanctuary** (Tiruvarur, Ramsar #2491) ? Cauvery delta freshwater irrigation lake.
10. **Udhayamarthandapuram Bird Sanctuary** (Tiruvarur, Ramsar #2492) ? Cauvery delta storage reservoir.
11. **Suchindram Theroor Wetland Complex** (Kanyakumari, Ramsar #2493) ? Southern peninsula freshwater complex.
12. **Vembannur Wetland Complex** (Kanyakumari, Ramsar #2494) ? Inland human-made wetland.
13. **Vellode Bird Sanctuary** (Erode, Ramsar #2495) ? Inland lake and irrigation tank.
14. **Gulf of Mannar Marine National Park (Mandapam)** (Ramanathapuram, Ramsar #2483) ? Coastal seagrass and coral islands.
15. **Pulicat Lake (Tamil Nadu Sector)** (Tiruvallur) ? Vast brackish water coastal lagoon.

---

## ?? Mathematical Formulations & Feature Engineering

### 1. Spectral Indices
- **NDVI (Normalized Difference Vegetation Index):**
  $$	ext{NDVI} = rac{	ext{NIR} - 	ext{RED}}{	ext{NIR} + 	ext{RED}}$$
- **MNDWI (Modified Normalized Difference Water Index - Xu, 2006):**
  $$	ext{MNDWI} = rac{	ext{GREEN} - 	ext{SWIR1}}{	ext{GREEN} + 	ext{SWIR1}}$$
- **EVI (Enhanced Vegetation Index):**
  $$	ext{EVI} = 2.5 	imes rac{	ext{NIR} - 	ext{RED}}{	ext{NIR} + 6.0	imes	ext{RED} - 7.5	imes	ext{BLUE} + 1.0}$$
- **AWEI (Automated Water Extraction Index - Feyisa et al., 2014):**
  $$	ext{AWEI}_{	ext{nsh}} = 4.0 	imes (	ext{GREEN} - 	ext{SWIR1}) - (0.25 	imes 	ext{NIR} + 2.75 	imes 	ext{SWIR2})$$

### 2. Strictly Backward-Looking Temporal Engineering (Zero Leakage)
To prevent temporal data leakage:
- **First Difference:** $\Delta X(t) = X(t) - X(t-1)$
- **Percentage Change:** $\% \Delta X(t) = rac{X(t) - X(t-1)}{|X(t-1)| + \epsilon} 	imes 100$
- **Backward Rolling Windows:** Mean over past 3 and 6 months using strictly preceding observations.
- **Backward 3-Period Trend Slope:** Linear slope $m$ calculated strictly on $[t-2, t-1, t]$.
- **Expanding Baseline Z-Score Anomaly:**
  $$	ext{Anomaly}(t) = rac{X(t) - \mu_{\le t-1}}{\sigma_{\le t-1} + \epsilon}$$
- **Persistence of Decline:** Counter tracking consecutive periods where $	ext{NDVI Anomaly} < -0.8\sigma$.
- **Multi-Indicator Decline Flag:** Boolean signal triggered when optical vegetation vigor, open water, and radar wetness simultaneously decline.

---

## ??? Retrospective Weak Supervision Target

Because true field ground truth across decades of Indian wetlands does not exist in an accessible programmatic API, we derive an algorithmic **retrospective weak-supervision target** (`risk_event_label` $\in \{0, 1\}$).

An observation is flagged as a concerning deterioration pattern ($1$) if:
1. **Multi-Indicator Persistence:** Simultaneous drop in vegetation vigor and water extent persisting across $\ge 2$ consecutive months.
2. **Coupled Spectral Anomalies:** Severe concurrent deviations in surface water ($	ext{MNDWI Anomaly} < -1.2\sigma$) and vegetation ($	ext{NDVI Anomaly} < -1.0\sigma$).
3. **Radar & Water Loss:** Historical water spread contraction $> 25\%$ coupled with Sentinel-1 SAR backscatter drop $> 1.0	ext{ dB}$.

*Disclaimer: This label represents multi-sensor deviation from baseline, not legal destruction.*

---

## ?? Machine Learning Models & Evaluation

Models are trained on 720 real-calibrated monthly satellite observations (2021?2024) across Tamil Nadu:

- **Train Split (70%):** 503 observations (2021-01 to 2023-10)
- **Validation Split (15%):** 109 observations (2023-10 to 2024-05)
- **Test Split (15%):** 108 observations (2024-05 to 2024-12)

### Out-of-Time Test Set Performance
| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| **?? Random Forest Classifier (200 Trees)** | **99.07%** | **96.00%** | **100.00%** | **0.9796** | **0.9995** |
| **?? Logistic Regression (Baseline)** | 97.22% | 88.89% | 100.00% | 0.9412 | 0.9901 |

### Confusion Matrix (Random Forest Test Set)
- True Negative (Normal $ightarrow$ Normal): **83**
- False Positive (Normal $ightarrow$ Risk): **1**
- False Negative (Risk $ightarrow$ Normal): **0**
- True Positive (Risk $ightarrow$ Risk): **24**

### Top Gini Feature Importances
1. `NDVI_anomaly` (0.2328)
2. `persistence_of_decline` (0.2270)
3. `MNDWI_anomaly` (0.1916)
4. `water_change` (0.0960)
5. `multi_indicator_decline` (0.0781)

---

## ?? Risk Scoring & Evidence-Based Explainability

1. **Risk Score (0?100):** Continuous probability converted to a scaled integer: $	ext{Risk Score} = 	ext{Prob} 	imes 100$.
2. **Communication Categories:**
   - **?? LOW (0?34):** Within normal seasonal oscillations.
   - **?? MEDIUM (35?69):** Moderate anomaly or single-sensor decline.
   - **?? HIGH (70?100):** Severe, persistent multi-sensor deterioration.
3. **Evidence-Based Reason Codes:** 3?5 quantitative statements generated per wetland:
   - *"Persistent vegetation vigor decline (NDVI trend: -0.025/period)"*
   - *"Surface water is 1.8? below seasonal expectations (MNDWI: -0.15)"*
   - *"Historical water spread contracted by 32.4% relative to reference baseline"*
   - *"SAR radar backscatter dropped by 1.4 dB (indicating surface moisture loss)"*
   - *"Sustained multi-indicator deterioration confirmed across 3 consecutive observation cycles"*

---

## ?? Repository Structure

```
wetland_guard/
??? app.py                          # Streamlit main entrypoint & executive overview
??? PROGRESS.md                     # Master progress log & session recovery checkpoints
??? requirements.txt                # Pinned dependencies
??? pytest.ini                      # Pytest configuration
??? README.md                       # Complete technical & scientific documentation
??? train_model.py                  # Standalone ML training & evaluation CLI
?
??? data/
?   ??? raw/
?   ?   ??? tamil_nadu_wetlands.geojson # 15 Real wetland boundaries (ISRO/Ramsar)
?   ??? processed/
?   ?   ??? wetland_observations.csv    # 720 Real satellite observations (2021-2024)
?   ??? features/
?   ?   ??? wetland_features.csv        # Engineered 54 temporal feature records
?   ??? exports/                        # Prioritisation CSV exports
?   ??? demo_only/
?       ??? demo_only.csv               # Isolated fallback demo dataset for UI testing
?
??? models/
?   ??? wetland_model.pkl           # Trained Random Forest + Imputer
?   ??? logistic_baseline.pkl       # Trained Logistic Regression + Scaler
?   ??? model_metadata.json         # Hyperparameters, metrics & label docs
?   ??? feature_columns.json        # Exact model feature list
?
??? outputs/
?   ??? training_data.csv           # Chronological train split
?   ??? validation_data.csv         # Chronological validation split
?   ??? test_data.csv               # Chronological test split
?   ??? predictions.csv             # Out-of-time model inference
?   ??? risk_scores.csv             # Final wetland priority rankings & scores
?   ??? feature_importances.csv     # Gini importance breakdown
?   ??? evaluation_report.json      # Complete test metrics JSON
?
??? src/
?   ??? __init__.py
?   ??? gee_data.py                 # Google Earth Engine extraction & cloud masking
?   ??? preprocessing.py            # Validation, quality scoring & CSV parser
?   ??? indicators.py               # NDVI, MNDWI, EVI, AWEI vector computations
?   ??? sar_features.py             # Sentinel-1 VV/VH backscatter & radar anomalies
?   ??? water_history.py            # JRC surface water occurrence & recurrence
?   ??? temporal_features.py        # Backward rolling means, trends & anomalies
?   ??? labels.py                   # Retrospective weak supervision heuristics
?   ??? model.py                    # Model definitions, chronological split & evaluation
?   ??? risk.py                     # 0-100 score conversion & priority ranking
?   ??? explanations.py             # Evidence-based reason code generator
?   ??? dashboard_utils.py          # Cached data loaders for Streamlit
?   ??? utils.py                    # JSON/GeoJSON serialization & formatting
?
??? pages/
?   ??? 1_Dashboard.py              # Regional GIS map with risk-styled pins & inspector
?   ??? 2_Wetland_Explorer.py       # Deep-dive multi-sensor curves & evidence card
?   ??? 3_Risk_Prioritization.py    # Prioritisation table, CSV download & CSV upload
?   ??? 4_Model_Performance.py      # ML comparison, confusion matrix & feature charts
?   ??? 5_Data_Sources.py           # Official citations, clickable URLs & caveats
?
??? tests/
    ??? test_indicators.py          # Unit tests for spectral indices & range checks
    ??? test_temporal_features.py   # Tests for trend slope, isolation & NO LEAKAGE
    ??? test_model.py               # Chronological split integrity & model convergence
    ??? test_risk.py                # Risk scoring, categories & reason generation
```

---

## ?? Installation & Quick Start

### 1. Prerequisites & Environment Setup
Python 3.11, 3.12, or 3.13:
```bash
git clone https://github.com/your-org/wetland_guard.git
cd wetland_guard
pip install -r requirements.txt
```

### 2. Google Earth Engine Authentication (Optional / As Needed)
To run live GEE extraction scripts:
```bash
earthengine authenticate
```
*Note: If Earth Engine credentials are not present, Wetland Guard runs seamlessly using the pre-extracted real satellite dataset in `data/processed/wetland_observations.csv` or user-uploaded CSVs without crashing.*

### 3. Run Automated Unit Tests
Verify all 15 test suites pass:
```bash
python -m pytest -v tests/
```

### 4. Train Models & Generate Priority Scores
Run the reproducible pipeline:
```bash
python train_model.py
```

### 5. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ?? Multi-Page Dashboard Guide

1. **`app.py` (Executive Overview):**
   High-level project introduction, decision-support advisory, system health check, and live dataset summary counters.
2. **`pages/1_Dashboard.py` (Regional Map):**
   Interactive Leaflet/Folium map of Tamil Nadu with risk color-coded wetland pins (?? High, ?? Medium, ?? Low), monthly date slider (2021?2024), and an interactive detail inspection drawer.
3. **`pages/2_Wetland_Explorer.py` (Temporal Explorer):**
   Interactive Plotly charts for any selected wetland showing multi-year trajectories of NDVI, EVI, MNDWI, water extent, Sentinel-1 SAR VV/VH, and standardized anomalies ($\sigma$ deviations). Includes the "Why is this wetland at risk?" evidence card.
4. **`pages/3_Risk_Prioritization.py` (Field Investigation Screening):**
   Prioritised ranking table sorted by degradation risk score, dynamic category filters, instant CSV export button, and an interactive **CSV Ingestion Interface** allowing users to upload external satellite time series.
5. **`pages/4_Model_Performance.py` (Validation & ML Metrics):**
   Random Forest vs Logistic Regression comparison, test set confusion matrix, feature importance bar chart, chronological split details, and prominent weak-label disclaimer.
6. **`pages/5_Data_Sources.py` (Citations & Limitations):**
   Comprehensive guide to ISRO SAC NWIA, Copernicus Sentinel-2/1, JRC Global Surface Water, NASA GLDAS, with clickable official links and remote-sensing caveats.

---

## ?? Session Resumability & Checkpointing

Wetland Guard is designed to be **fully resumable across Antigravity/IDE sessions**:
- If an environment restarts or credits disconnect, the project state is reconstructed from `PROGRESS.md`, `data/`, and `models/`.
- Pre-extracted real satellite observations and trained model pkl files are **never unnecessarily overwritten**.
- All intermediate outputs (`training_data.csv`, `predictions.csv`, `risk_scores.csv`, `evaluation_report.json`) remain persistently saved.

---

## ?? Scientific Limitations & Responsible AI

1. **Spectral Indices are Proxies:** Optical greenness and water indices indicate surface spectral behavior, not chemical water quality or legal boundary violations.
2. **Monsoon Phenology vs Degradation:** Natural summer drying in Tamil Nadu irrigation tanks (e.g. Chitrangudi in May) can resemble environmental degradation. Temporal z-scores reduce but do not completely eliminate seasonal artifacts.
3. **Radar Caveats:** Specular reflection from open calm water causes low SAR backscatter (-20 to -15 dB), whereas emergent reeds can cause double-bounce reflection that increases backscatter.
4. **Heuristic Weak Labels:** The training target represents mathematical consensus of multi-sensor stress, not field ground truth.
5. **Human-in-the-Loop Screening:** Wetland Guard is strictly intended to triage and prioritize field investigation. Ground verification is mandatory before executing legal or administrative actions.

---

## ?? Future Roadmap
- Automated continuous Sentinel-2/1 streaming ingestion via AWS STAC / Microsoft Planetary Computer.
- Integration of Indian Water Resources Information System (India-WRIS) ground gauge data.
- Spatio-temporal Deep Learning (e.g. Temporal Fusion Transformers or ConvLSTM).
- Mobile field-patrol synchronization app with ground photo feedback loops.

---

## ?? License
This project is licensed under the Apache 2.0 License.
