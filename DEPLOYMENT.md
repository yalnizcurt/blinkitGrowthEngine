# 🚀 Cloud Deployment Guide: Railway (Backend) + Vercel (Frontend)

This guide provides step-by-step instructions for deploying the **Blinkit Customer Discovery Engine & Web Dashboard** to Railway and Vercel.

---

## 🏗️ Deployment Architecture

| Component | Platform | URL Pattern | Responsibility |
|---|---|---|---|
| **Backend API** | **Railway** | `https://<your-railway-app>.up.railway.app` | Runs Python backend, NLP clustering (`sentence-transformers`, `bertopic`), Groq/LLaMA RAG engine, live scrapers, and REST APIs (`/api/*`). |
| **Frontend UI** | **Vercel** | `https://<your-vercel-app>.vercel.app` | Hosts static Web Dashboard UI (`static/index.html`, `app.js`) and proxies `/api/*` requests seamlessly to Railway backend. |

---

## 🛠️ Step 1: Deploy Backend on Railway

1. **Sign in to Railway**:
   - Go to [railway.app](https://railway.app) and link your GitHub account.

2. **Create New Project**:
   - Click **"New Project"** → **"Deploy from GitHub repo"**.
   - Select your repository: `yalnizcurt/blinkitGrowthEngine`.

3. **Configure Environment Variables**:
   - In Railway, navigate to your service → **Variables** tab.
   - Add the following environment variable:
     - `GROQ_API_KEY`: `gsk_...` (Your Groq API key)
     - `LLM_MODEL`: `llama-3.1-8b-instant`
     - `PORT`: `8080` (Optional, Railway automatically sets `$PORT`)

4. **Generate Public Domain**:
   - In Railway, go to **Settings** → **Networking** → Click **"Generate Domain"**.
   - Copy your live HTTPS domain (e.g., `https://blinkitgrowthengine-production.up.railway.app`).

---

## 🌐 Step 2: Deploy Frontend on Vercel

1. **Sign in to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in.

2. **Import Repository**:
   - Click **"Add New..."** → **"Project"**.
   - Import `yalnizcurt/blinkitGrowthEngine`.

3. **Configure Vercel Settings**:
   - **Framework Preset**: Select **Other** / **Static Site**.
   - **Root Directory**: `./` (leave default).

4. **Configure Proxy in `vercel.json`**:
   - The repository already includes `vercel.json` configured with reverse proxy rewrites:
     ```json
     {
       "version": 2,
       "cleanUrls": true,
       "rewrites": [
         {
           "source": "/api/(.*)",
           "destination": "https://<your-railway-app>.up.railway.app/api/$1"
         },
         {
           "source": "/(.*)",
           "destination": "/static/$1"
         }
       ]
     }
     ```
   - *Note*: Ensure the `destination` domain in `vercel.json` matches your generated Railway URL!

5. **Deploy**:
   - Click **"Deploy"**. Vercel will publish your live dashboard.

---

## 📦 Deployment Config Files Included

- `railway.json`: Railway builder configuration pointing to `Dockerfile`.
- `Dockerfile`: Production Python 3.11-slim container with required NLP dependencies.
- `Procfile`: Process definition (`web: python server.py`).
- `vercel.json`: Vercel static routing and Railway API proxy rewrite configuration.
- `server.py`: CORS preflight enabled (`do_OPTIONS` handler) HTTP REST API.

---

## 💻 Local Testing & Execution

To run locally before or alongside deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Run Web Dashboard & API Server
python3 server.py
```
Open [http://localhost:8080](http://localhost:8080) in your browser.
