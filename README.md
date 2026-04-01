
# 🌍 NewSpace Hybrid Digital Twin Platform

## A Physics-Informed Multi-Sensor AI Framework for Predictive Risk Intelligence


## 🏷️ Badges

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)
![AI](https://img.shields.io/badge/AI-Deep%20Learning%20%7C%20Geospatial-purple.svg)
![Digital Twin](https://img.shields.io/badge/Digital%20Twin-Hybrid%20Multi--Sensor-critical)
![CI](https://img.shields.io/github/actions/workflow/status/civiastech/newspace-hybrid-digital-twin/ci.yml?branch=main)
![Last Commit](https://img.shields.io/github/last-commit/civiastech/newspace-hybrid-digital-twin)
![Stars](https://img.shields.io/github/stars/civiastech/newspace-hybrid-digital-twin?style=social)



## ⚡ Executive Overview

> A **hybrid digital twin system** that fuses **satellite, UAV, terrain, and sensor data** into a **time-evolving AI-powered risk intelligence engine**.

This platform transforms fragmented monitoring into:

* 📊 Continuous situational awareness
* 🧠 AI-driven decision intelligence
* ⚠️ Early warning for infrastructure & environmental risks


## 🎯 Problem Statement

Current monitoring systems are:

* ❌ Surface-level
* ❌ Disconnected across sensors
* ❌ Reactive instead of predictive

Critical processes like:

* slope instability
* wildfire impact propagation
* subsurface degradation

remain **undetected until failure**.



## 💡 Solution

The NewSpace platform introduces:

✔ Multi-sensor integration
✔ AI-driven feature extraction
✔ Uncertainty-aware fusion
✔ Time-aware digital twin
✔ Decision-support outputs



# 🧠 SYSTEM ARCHITECTURE

```mermaid
flowchart LR

A[Satellite Data<br/>Sentinel-1/2] --> B[Ingestion]
C[UAV Imagery] --> B
D[Terrain DEM] --> B
E[IoT Sensors] --> B

B --> F[Validation & QA]
F --> G[Preprocessing & Alignment]

G --> H[Feature Engineering]
H --> I[Dataset Builder]

I --> J[AI Models]
J --> K1[Segmentation]
J --> K2[Severity Classification]
J --> K3[Anomaly Detection]

K1 --> L[Multi-Modal Fusion]
K2 --> L
K3 --> L

L --> M[Uncertainty + Consistency]

M --> N[Digital Twin Engine]
N --> O[Risk Score]
N --> P[Priority Ranking]
N --> Q[Recommended Actions]

Q --> R[Decision Support Outputs]
```


# 🔄 PIPELINE FLOW

```mermaid
graph TD

A[Raw Data] --> B[Ingestion]
B --> C[Validation]
C --> D[Preprocessing]
D --> E[Feature Extraction]
E --> F[Dataset Creation]
F --> G[Model Training]
G --> H[Prediction]
H --> I[Fusion]
I --> J[Digital Twin Update]
J --> K[Risk Outputs]
```


# 🧩 CORE MODULES

| Module            | Description                    |
| ----------------- | ------------------------------ |
| **Ingestion**     | Multi-source data loading      |
| **Validation**    | Data quality checks            |
| **Preprocessing** | Alignment & cleaning           |
| **Features**      | Multi-modal feature extraction |
| **Datasets**      | Training-ready data            |
| **Models**        | AI training & inference        |
| **Fusion**        | Multi-sensor integration       |
| **Twin**          | State evolution engine         |
| **Experiments**   | Benchmarking & analysis        |
| **Outputs**       | Reports & geospatial outputs   |


# 🧠 AI COMPONENTS

* 🔍 Segmentation (burn area, defects)
* 📊 Severity Classification
* ⚠️ Anomaly Detection (sensor signals)
* 🔗 Multi-modal fusion scoring
* 📉 Calibration & uncertainty estimation

# 🔬 RESEARCH INNOVATION

### Key Contribution:

> **UM-SWRI (Uncertainty-aware Multi-Sensor Severity-Weighted Risk Index)**

This combines:

* AI predictions
* sensor signals
* temporal dynamics
* uncertainty

into a **single decision-ready metric**.


# 🔥 USE CASE: WILDFIRE DIGITAL TWIN

* Burn severity mapping
* SAR change detection
* Multi-modal risk fusion
* Temporal state tracking


# ⚙️ INSTALLATION

```bash
git clone https://github.com/civiastech/newspace-hybrid-digital-twin
cd newspace-hybrid-digital-twin

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```


# ▶️ RUN PIPELINE

```bash
python -m newspace_twin.pipeline --stage all
```



# 🧪 TESTING

```bash
pytest
```


# 📊 OUTPUTS

* 📍 GeoJSON risk maps
* 📄 CSV predictions
* 📈 Benchmark reports
* 📉 Calibration plots
* 🧠 Digital twin state logs


# 📈 PROJECT STATUS

| Component             | Status       |
| --------------------- | ------------ |
| Architecture          | ✅ Complete   |
| Training Pipeline     | ✅ Working    |
| Prediction Export     | ✅ Working    |
| Fusion System         | 🚧 Improving |
| Real Data Integration | 🚧 Ongoing   |
| Deployment            | 🔜 Planned   |


# 🧑‍💻 PROJECT LEADERSHIP

* Civil Engineer (COREN)
* AI Researcher
* Digital Twin Architect


# 🤖 ROLE OF AI

AI acts as the **core integrator**:

* learns from heterogeneous data
* bridges sensing gaps
* quantifies uncertainty
* drives decisions


# 🤝 FUNDING & COLLABORATION

We are open to:

* 🇪🇺 Horizon Europe / ERC / FCT
* 🏗 Infrastructure companies
* 🌍 Government partnerships
* 🔬 Research institutions


# 🌐 VISION

> To build a **globally scalable, intelligent digital twin system**
> for infrastructure and environmental risk management.


# ⭐ SUPPORT THE PROJECT

If you believe in this vision:

```md
⭐ Star this repo  
🍴 Fork it  
🤝 Collaborate  
```


# ⚡ FINAL STATEMENT

This is not just a repository.

> It is a **research platform for the future of intelligent infrastructure systems**.



