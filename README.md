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

## Project structure

\go-safe\
├── .env                    # Environment variables (MIMIK_TOKEN, OPENAI KEY, LANGCHAIN)
├── venv                    # virtual environment
├── data\                   # Data directory
│   ├── evacuation_db\      # ChromaDB local storage
│   ├── synthetic_data.json  # Original synthetic data
│   ├── processed_data.json  # mimik-processed data
│   └── cached_plans.json   # Precomputed offline plans
├── model.py           # Standalone RAG logic
├── generate_cached_plans.py  # Script to create cached_plans.json
├── .gitignore
├── mimik_process.py  # Script to process synthetic data
└── README.md               # This file

## Setup Instructions

1. **Clone or Prepare Directory**
   ```bash
   git clone https://github.com/Abdulrahman0044/go-safe.git

1. **Configure Environment**
   - Create `.env` in the root directory:

   MIMIK_TOKEN=your-mimik-token-here
   OPENAI_API_KEY=your-openai-api-key-here  # Optional
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_API_KEY="replace with your actual api key"
   LANGCHAIN_PROJECT="pr-reflecting-starter-78"

1. **Generate Data (If Missing)**
- **Synthetic Data**: If `synthetic_data.json` isn’t present, refer to earlier steps to generate it with Ollama/LangChain (not included here).
- **Processed Data**: Run:
```bash
python simulate_mimik_processing.py