# 📈 Stock Sentiment Analyzer

[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-46C3B9?logo=render)](https://render.com)
[![GitHub Actions](https://github.com/pathak-sketch/stock-sentiment-pro/actions/workflows/deploy.yml/badge.svg)](https://github.com/pathak-sketch/stock-sentiment-pro/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A **real-time stock sentiment analysis platform** that captures tweets about major stocks, analyzes sentiment using AI (FinBERT/TextBlob), and presents interactive dashboards. Built with **FastAPI**, **React**, **PostgreSQL**, and **Docker**, with **CI/CD** pipelines and cloud deployment.

👉 **Live Demo:** [stock-sentiment-dashboard.onrender.com](https://stock-sentiment-dashboard.onrender.com)

---

## ✨ Features

- 📡 **Real‑time Twitter streaming** – Collects tweets mentioning stock symbols ($TSLA, $AAPL, …)
- 🧠 **AI‑powered sentiment analysis** – FinBERT and TextBlob for accurate financial sentiment
- 🎨 **Beautiful dashboard** – Material‑UI, real‑time charts, live tweet feed
- ⚡ **WebSocket updates** – Live sentiment changes without page refresh
- 🗄️ **Time‑series database** – PostgreSQL with TimescaleDB for efficient storage
- 🐳 **Dockerized deployment** – One‑command local setup and production builds
- 🔁 **CI/CD pipeline** – GitHub Actions test & deploy on every push
- ☁️ **Cloud ready** – Deploy to Render, AWS, or any Docker host

---

## 🛠️ Tech Stack

| Layer          | Technologies |
|----------------|--------------|
| **Backend**    | FastAPI, Python, WebSockets, Uvicorn |
| **Frontend**   | React, Material‑UI, Recharts, Axios |
| **Database**   | PostgreSQL, TimescaleDB, Redis (caching) |
| **ML / NLP**   | FinBERT, Transformers, TextBlob |
| **Streaming**  | Twitter API v2, Kafka (optional) |
| **DevOps**     | Docker, Docker Compose, GitHub Actions, Render |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop (for PostgreSQL)
- Twitter Developer Account (for real data)

### 1. Clone the repository
```bash
git clone https://github.com/pathak-sketch/stock-sentiment-pro.git
cd stock-sentiment-pro