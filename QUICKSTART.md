# Quick Start Guide

## 🚀 Get Running in 2 Minutes

### Terminal 1: Backend

```bash
cd play-store-scraper
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python backend/main.py
```

**Wait for:** `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend

```bash
cd play-store-scraper/frontend
python -m http.server 8001
```

**Then open in browser:** http://localhost:8001

---

## ✅ Test It

1. Paste this URL: `https://play.google.com/store/apps/details?id=com.lendingplate`
2. Keep dates as today
3. Leave hint empty
4. Click "Start Scraping"
5. Wait for results
6. Download Excel

---

## 📋 File Locations

- **Backend**: `backend/main.py`
- **Frontend**: `frontend/index.html`
- **Downloads**: `output/` folder

---

## 🐛 Issues?

- **Port 8000 in use**: `python backend/main.py --port 8001`
- **Can't connect**: Make sure both terminals are running
- **No reviews**: Try different date or remove hint
