# GoSafe - AI-Powered Offline Evacuation Planner

## Overview

*GoSafe* is an AI-driven mobile application designed to provide real-time, offline-first evacuation plans during wildfires, addressing the critical need for resilient emergency response systems. *GoSafe* leverages distributed edge computing and personalized AI to deliver fast, adaptive, and accessible evacuation routes—without relying on cloud infrastructure. This project was developed to tackle the challenges of network failures and user-specific needs in disaster scenarios like the recent Los Angeles fire.

---

## Problem Statement

Wildfires expose a critical gap in emergency response: centralized, cloud-dependent systems fail when networks and power grids collapse, delaying life-saving evacuation guidance. Vulnerable populations (e.g., wheelchair users) are underserved by generic plans. *GoSafe* solves this by:
- Operating offline on edge devices.
- Processing data locally with mimik’s edge computing.
- Providing personalized plans via Kwaai’s AI framework (proxied by OpenAI for now).

**Challenges**:
- Network outages hinder real-time updates.
- Balancing local scalability and autonomy.
- Tailoring plans to individual needs.
- Delivering a prototype by March 5, 2025, as a solo effort.

---

## Solution

*GoSafe* integrates:
- **mimik**: Edge computing for local data processing and peer-to-peer sync.
- **ChromaDB**: Local vector storage for 1,200 wildfire scenarios.
- **Kwaai/OpenAI**: Personalized evacuation plans via Retrieval-Augmented Generation (RAG).
- **LangChain & OllamaEmbeddings**: Local embedding and query handling.

The core logic resides in `model.py`, a standalone module that a mobile developer can integrate into a cross-platform app (e.g., Kivy). It processes queries offline using cached plans, with optional OpenAI enhancement when online.

---

## Features

- **Offline-First**: Runs fully on-device with ChromaDB and cached responses.
- **Personalized Plans**: Adapts routes to user needs (e.g., wheelchair access).
- **Edge Resilience**: Uses mimik for local processing and device collaboration.
- **Mobile-Ready**: Designed for deployment as an Android/iOS app.

---

## Prerequisites

- **Python 3.8+**
- **Dependencies**:
  ```bash
  pip install chromadb langchain langchain-community langchain-openai python-dotenv
- **Ollama**: Local LLaMA 3.1 for embeddings (`ollama pull llama3.1`, `ollama serve`).
- **mimik SDK**: Obtain from [developer.mimik.com](https://developer.mimik.com/).
- **OpenAI API Key**: Optional, from [platform.openai.com](https://platform.openai.com/).

---

## Project structure

```
go-safe\
├── .env                    # Environment variables (MIMIK_TOKEN, OPENAI KEY, LANGCHAIN)
├── venv                    # Virtual environment
├── data\                   # Data directory
│   ├── evacuation_db\      # ChromaDB local storage
│   ├── synthetic_data.json  # Original synthetic data
│   ├── processed_data.json  # Mimik-processed data
│   └── cached_plans.json   # Precomputed offline plans
├── model.py                # Standalone RAG logic
├── app.py                  # backend logic
├── generate_cached_plans.py # Script to create cached_plans.json
├── .gitignore
├── mimik_process.py        # Script to process synthetic data
└── README.md               # This file

```

---

## Setup Instructions

1. **Clone or Prepare Directory**
   ```bash
   git clone https://github.com/Abdulrahman0044/go-safe.git

1. **Configure Environment**
   - Create `.env` in the root directory:

   ```
    MIMIK_TOKEN=your-mimik-token-here
    OPENAI_API_KEY=your-openai-api-key-here  # Optional
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY="replace with your actual api key"
    LANGCHAIN_PROJECT="pr-reflecting-starter-78"
    ```

1. **Generate Data (If Missing)**
- **Synthetic Data**: If `synthetic_data.json` isn’t present, Run:
```bash
cd data && python data.py
```

- **Processed Data**: Run, if the data is not found:
```bash
python mimik_process.py
```

- **Cached Data**: Run, if the data is not found:
```bash
python generate_cached_plans.py
```

---

## Usage

### Standalone Testing

In Python:

```python
from model import EvacuationPlanner

planner = EvacuationPlanner()
plan = planner.get_evacuation_plan("Evacuate from Downtown LA, fire on Highway 101", "wheelchair")
print(plan)
```

### Mobile Integration (Flutter)

- **Input:** Pass `query` (string) and `user_needs` (string, default "none") to `get_evacuation_plan`.
- **Output:** Returns a string (plan or error).
- **Dependencies:** Bundle `evacuation_db/` and `cached_plans.json` with the app

---

## Deployment Notes for Mobile Developer (Flutter)

### Framework

- **Flutter**: Dart-based framework for Android/iOS.
- **Install**: [flutter.dev](https://flutter.dev).
- **Setup**: Install Flutter SDK, Dart, and an IDE (e.g., VS Code, Android Studio).

### Basic Flutter Example

#### Create a Flutter Project:

```bash
flutter create gosafe_app
cd gosafe_app
```

#### Update `pubspec.yaml`:

```yaml
name: gosafe_app
description: GoSafe Evacuation Planner

dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0  # Optional for online API calls

flutter:
  assets:
    - assets/cached_plans.json
```

#### Copy `cached_plans.json`:

Place `path to ./data/cached_plans.json` into `gosafe_app/assets/`.

### Build APK:

```bash
flutter run --release
```

Or:

```bash
flutter build apk
```

---

### Requirements

Included in `requirements.txt`:

```
chromadb
langchain
langchain-community
langchain-openai
python-dotenv
```

### Bundle:

- `evacuation_db/`
- `cached_plans.json`
- `.env` (with `MIMIK_TOKEN`)

### mimik Integration

- Replace `process_with_mimik` placeholder with actual SDK calls (see mimik mobile docs).
- Ensure mimik’s `edgeEngine` runs on-device.

### Offline vs. Online

- **Offline**: Uses ChromaDB and `cached_plans.json`.
- **Online**: Enable Groq with `ONLINE_MODE=1` env var.
- **Online (Optional)**: Run `model.py` as a local server (e.g., Flask) on your machine, call via HTTP:
```bash
python app.py
```

