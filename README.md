# AI-Powered SaaS Backend 🚀

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![Inference](https://img.shields.io/badge/AI-DistilGPT2-yellow)

## 📖 Overview

A production-ready **AI-Native SaaS Backend** built with **FastAPI**. It features a built-in **Local LLM (DistilGPT-2)** for text generation, fully integrated with **usage tracking**, **rate limiting**, and **billing**.

Perfect for engineers building monetized AI platforms using local resources.

## ✨ Key Features

-   **🤖 Local AI Service**: Embedded **Hugging Face** model (DistilGPT-2) for text generation. Includes **Mock Mode** for fast testing.
-   **💰 Smart Billing**: Tracks token/request usage per tenant and generates monthly invoices.
-   **🛡️ Rate Limiting**: Redis-backed sliding window limiter (default: 5 req/sec).
-   **🔐 Auth**: JWT for Users, Hashed API Keys for Services.
-   **⚡ Async Performance**: Non-blocking usage logging via background tasks.

## 🛠️ Tech Stack

-   **Core**: FastAPI, Python 3.9+
-   **AI**: Hugging Face Transformers, PyTorch
-   **Data**: PostgreSQL (Async), Redis
-   **Deploy**: Docker Compose

## 🚀 Quick Start

1.  **Start Services** (Default: Mock AI Mode):
    ```bash
    docker-compose up --build -d
    ```

2.  **Run Migrations**:
    ```bash
    docker-compose exec web alembic upgrade head
    ```

3.  **Test It**:
    ```bash
    pip install httpx
    python verify_system.py
    ```

> **Note**: To run the *real* AI model (downloads ~500MB), edit `docker-compose.yml` and set `MOCK_AI_MODEL=false`.
