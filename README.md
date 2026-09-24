# EcoTrace AI

**Evidence-based e-waste traceability and compliance verification**

> Prototype v0.1 — CV/OCR outputs are mocked for architecture validation.
> All data is synthetic and does not represent real-world statistics.

---

## Project Overview

EcoTrace AI is a functional prototype of an e-waste traceability and compliance
verification platform. It demonstrates the complete evidence-verification pipeline
from collection through processing, culminating in a Trust Badge decision.

The platform addresses a critical gap in e-waste compliance: a facility can
receive an item, pass evidence checks, and still never actually process it.
EcoTrace separates intake evidence quality (Trust Score) from processing
completion proof (Processing Completion Gate) — both are required before a
Trust Badge can be issued.

---

## Architecture

```
Data Capture  (Stage 0–1: Picker registration + collection)
     ↓
Identity & State  (Stage 2)
     ├── INTACT     →  OCR / Serial IMEI
     └── DISMANTLED →  CV Component Classification (PCB / Battery / Casing / Cable)
     ↓
Evidence Assembly  (Stage 3: GPS · Image Quality · Weight · Facility)
     ↓
Transport + Facility Intake  (Stage 4–5)
     ↓
Trust Score Engine  (Stage 6: Weighted formula — mode determined at Stage 2)
     ↓
Processing Completion Gate  (Stage 7: HARD GATE — must pass independently)
     ↓
Narration Generation  (Stage 8: blocked if Stage 7 fails)
     ↓
Narration Confidence  (Stage 9: regulatory grounding + consistency scoring)
     ↓
Trust Badge  (Stage 10: AUTO-ISSUED / HITL REVIEW / REJECTED)
     ↓
Audit Dashboard  (Stage 11: Facility patterns, anomaly flags)
```

---

## Trust Score Formulas

### Mode A — Intact Item

| Component                     | Weight |
|-------------------------------|--------|
| Serial / IMEI OCR Confidence  | 30%    |
| Serial Uniqueness             | 15%    |
| Facility Registration Validity| 20%    |
| GPS Validity                  | 15%    |
| Image Quality                 | 10%    |
| Weight Consistency            | 10%    |

```
Trust Score = (OCR × 0.30) + (Serial Uniqueness × 0.15) + (Facility × 0.20)
            + (GPS × 0.15) + (Image × 0.10) + (Weight × 0.10)
```

### Mode B — Dismantled Item

| Component                             | Weight |
|---------------------------------------|--------|
| Component Classification Confidence   | 30%    |
| Material Composition Plausibility     | 15%    |
| Facility Registration Validity        | 20%    |
| GPS Validity                          | 15%    |
| Image Quality                         | 10%    |
| Weight Consistency                    | 10%    |

```
Trust Score = (Component Confidence × 0.30) + (Material Plausibility × 0.15)
            + (Facility × 0.20) + (GPS × 0.15) + (Image × 0.10) + (Weight × 0.10)
```

**Important:** Dismantled items are NOT penalised for missing serial/IMEI.
The weighting mode is fixed at Stage 2 and cannot be changed.

### Trust Score Thresholds

| Score     | Status         |
|-----------|----------------|
| ≥ 0.80    | AUTO-VERIFIED  |
| 0.55–0.79 | HITL REVIEW    |
| < 0.55    | REJECTED       |

---

## Stage 7 — Processing Completion Gate

**This is the most important architectural decision in EcoTrace.**

A high Trust Score proves that collection and intake evidence is reliable.
It does NOT prove that the item was actually processed or destroyed.

The Processing Completion Gate is a hard gate that requires:

1. **Processing completion evidence has been submitted** — destruction or
   dismantling proof must exist independently of intake evidence.
2. **Evidence was submitted within the 72-hour time window** — late submissions
   are flagged for HITL review.

Both conditions must be true. If either fails:
- Trust Badge is **not issued**
- Narration generation is **blocked**
- Record is held for HITL review

**Demo scenario:** Set Trust Score inputs high (score ~0.94, AUTO-VERIFIED),
then toggle Completion Evidence to OFF. The score stays AUTO-VERIFIED but the
gate fails and the badge is not issued. This is the key demo moment.

---

## Local Setup

### Prerequisites

- Python 3.9 or later
- pip

### Install dependencies

```bash
cd ecotrace-ai
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## File Structure

```
ecotrace-ai/
├── app.py                        # Main entry point, routing, global CSS
├── config.py                     # All weights, thresholds, constants
├── requirements.txt
│
├── data/
│   ├── mock_transactions.json    # 20 synthetic verification records
│   ├── mock_facilities.json      # 5 synthetic processing facilities
│   └── mock_regulations.json     # Synthetic regulatory references
│
├── services/
│   ├── trust_score.py            # Core Trust Score calculation engine
│   ├── mock_cv.py                # Mock computer vision service
│   ├── mock_ocr.py               # Mock OCR service
│   ├── processing_gate.py        # Stage 7 hard gate logic
│   ├── narration.py              # Narration generation (mock)
│   └── anomaly_detection.py      # Rule-based facility anomaly detection
│
├── components/
│   ├── sidebar.py                # Navigation sidebar
│   ├── pipeline.py               # 12-stage pipeline visualisation
│   ├── score_card.py             # Trust Score card with SVG ring
│   ├── evidence_card.py          # Evidence metrics display
│   ├── processing_gate.py        # Processing gate card
│   ├── badge.py                  # Trust Badge card
│   └── charts.py                 # Plotly audit charts
│
├── pages/
│   ├── dashboard.py              # Evidence Verification Overview
│   ├── verification.py           # New Verification workflow (main page)
│   ├── history.py                # Verification History
│   ├── audit.py                  # Audit Dashboard
│   └── architecture.py           # System Architecture explainer
│
└── utils/
    ├── formatting.py             # Status colours, indicators, HTML helpers
    └── demo_presets.py           # 4 demo scenario presets
```

---

## Demo Scenarios

### Preset 1 — Successful Dismantled Item
- Item: Dismantled PCB, confidence 94%
- All evidence high, completion evidence submitted, within window
- **Expected:** Trust Score ~0.94, Gate PASSED, Badge AUTO-ISSUED

### Preset 2 — High Trust but No Processing Proof ⭐ (Key Demo)
- Same high evidence as Preset 1
- Completion evidence: **OFF**
- **Expected:** Trust Score AUTO-VERIFIED **BUT** Gate FAILED, Narration BLOCKED, Badge NOT ISSUED

### Preset 3 — Low Evidence Quality
- Component confidence 45%, GPS 50%, Image 50%, Weight 55%
- **Expected:** Trust Score < 0.55, REJECTED

### Preset 4 — Intact Device
- Item: Intact, OCR confidence 92%, Serial Uniqueness 100%
- **Expected:** Intact-mode Trust Score calculation, Badge AUTO-ISSUED

### Recommended 3–5 Minute Demo Flow

1. Open **Dashboard** — show pipeline and KPI cards
2. Click **New Verification**
3. In Demo Controls, load **Preset 1** — show score 0.94, gate PASSED, badge issued
4. Load **Preset 2** — show same high score but gate FAILED, badge NOT ISSUED
5. Toggle Completion Evidence back ON — watch gate turn PASSED and badge appear
6. Open **Audit Dashboard** — show facility patterns and anomaly flags

---

## Current Limitations

- **No real CV model.** Component classification confidence is set manually via
  demo controls. `mock_cv.py` must be replaced with a trained classifier.
- **No real OCR.** Serial numbers are from a synthetic pool. `mock_ocr.py` must
  be replaced with a real OCR service.
- **No real LLM.** Compliance narration is template-generated. `narration.py`
  must be replaced with a RAG + LLM pipeline.
- **No database.** All data is loaded from local JSON files. A real deployment
  would use a persistent store.
- **Anomaly detection is rule-based.** Not a trained model.
- **No authentication.** This is a demo prototype — no user accounts or access
  control are implemented.

---

## Future ML Integration Plan

The codebase is designed so that mock services can be swapped for real
implementations with no changes to the Trust Score engine or pipeline logic.

### Replace mock_cv.py

```python
# Future interface (same as mock)
def predict_component(image) -> dict:
    # Load trained CNN / ViT model
    # Run inference on image
    return {
        "component":  "PCB",       # one of: PCB / Battery / Casing / Cable
        "confidence": 0.94,
        "mode":       "REAL",
    }
```

### Replace mock_ocr.py

```python
# Future interface (same as mock)
def run_ocr(image) -> dict:
    # Call real OCR service (Tesseract / cloud OCR / fine-tuned model)
    return {
        "serial":            "SN-REAL-12345",
        "confidence":        0.92,
        "serial_uniqueness": 1.0,
        "mode":              "REAL",
    }
```

### Replace narration.py

Replace `generate_narration()` with a call to an LLM + RAG pipeline that
retrieves relevant regulatory clauses and generates grounded narration.

The `gate_passed` check at the top of the function must be preserved —
narration should only be generated after Stage 7 passes.

### Trained Anomaly Detection

Replace the rule-based logic in `anomaly_detection.py` with a trained
anomaly-detection model (e.g., Isolation Forest, Autoencoder) trained on
historical facility patterns.

---

## Honesty Notice

This prototype clearly indicates that:

- All CV/OCR predictions are mocked
- All data records are synthetic
- Narration is template-generated, not LLM-produced
- Anomaly detection is rule-based, not a trained model

No claims of model accuracy are made. The purpose of this version is
architecture validation and pipeline demonstration.
