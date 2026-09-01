# SatyaKavach — Deployment Guide (Vercel + Render, 100% Free)

> Goal: give hackathon judges a live, public URL for the web app.
> Estimated first-time setup: **2.5–4 hours**. Re-deploys after that: **5–10 min** (auto from GitHub).

## Architecture

```
Judges' browser
   │
   ▼
https://<your-app>.vercel.app   (Frontend PWA - React, built with VITE_API_URL)
   │  axios /api/v1/...
   ▼
https://<your-backend>.onrender.com   (FastAPI backend)
   ├─ Neon Postgres (database)
   └─ Cloudflare R2 (media storage) — optional; backend falls back to local disk
```

---

## Prerequisites (accounts you need)

Create these free accounts (sign in / sign up):

| # | Service | Purpose | Sign-up URL |
|---|---------|---------|-------------|
| 1 | GitHub | Host the code | github.com |
| 2 | Vercel | Host the frontend | vercel.com |
| 3 | Render | Host the backend API | render.com |
| 4 | Neon | Managed Postgres DB | neon.tech |
| 5 | Cloudflare R2 | Media storage (optional) | dash.cloudflare.com |

You also need one **Gemini API key** (free) from https://aistudio.google.com/apikey

---

## Step 1 — Push code to GitHub (10–15 min)

The repo is already connected to `https://github.com/Aicodebyprince/SatyaKavach.git`.

From a terminal in this folder:

```powershell
git add -A
git commit -m "Prepare production deployment (Render + Vercel configs)"
git push origin <your-branch>
```

> ⚠️ `.env` is git-ignored, so the real Gemini key stays off GitHub. You'll paste keys
> into Render/Vercel dashboards instead. Never force-add `.env`.

---

## Step 2 — Create the database on Neon (10–15 min)

1. Go to **neon.tech** → **Create a project** → name it `satyakavach`.
2. Copy the **connection string**:
   `postgresql://<user>:<password>@<region>.neon.tech/satyakavach?sslmode=require`
3. Save it — you'll paste it into Render.

---

## Step 3 — Deploy the backend on Render (30–60 min)

1. Go to **render.com** → **New** → **Blueprint**.
2. Connect your GitHub repo. Render reads `backend/render.yaml` and creates the web service automatically.
3. In the service's **Environment** tab, set these values:

   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | The Neon connection string from Step 2 |
   | `GEMINI_API_KEY` | Your free Gemini key |
   | `S3_ENDPOINT` | `https://<account>.r2.cloudflarestorage.com` (R2) — or leave blank |
   | `S3_ACCESS_KEY` | Your R2 access key (or blank) |
   | `S3_SECRET_KEY` | Your R2 secret key (or blank) |
   | `REDIS_URL` | Leave blank (not needed) |

4. Click **Apply / Deploy**. First build takes ~10-20 min (installs `onnxruntime`, `opencv`, etc.).
5. When live, Render gives you a URL like `https://satyakavach-api.onrender.com`.
   - Test it: open `https://<your-url>/health` → should return `{"status":"healthy",...}`.

> ℹ️ `DEMO_MODE=true` is set so the app works with **zero model weights** and mock-but-realistic
> AI scores. No ONNX files need uploading (they're git-ignored).

---

## Step 4 — Deploy the frontend on Vercel (15–30 min)

1. Go to **vercel.com** → **Add New Project** → import your GitHub repo.
2. Vercel auto-detects the frontend via `frontend/vercel.json` (root = `frontend`). If asked, set:
   - **Root Directory**: `frontend`
3. Before deploying, add one **Environment Variable**:
   - Name: `VITE_API_URL`
   - Value: `https://<your-backend>.onrender.com` (from Step 3)
   - Apply to **Production** (and Preview if you want).
4. Click **Deploy**. ~2-5 min.
5. When done you get `https://<your-app>.vercel.app`.

---

## Step 5 — Test end-to-end (30 min)

On the live Vercel URL:

1. **Anonymous flow**: upload an image → should return a Trust Score + verdict.
2. **Link check**: submit a suspicious URL.
3. **Audio**: upload a voice clip.
4. **Register/login**: create an account, check history.

Common issues:

| Symptom | Fix |
|---------|-----|
| Browser console shows CORS errors | `CORS_ORIGINS` in Render should be `*` (already set in `render.yaml`), or add your exact Vercel URL |
| `VITE_API_URL` not applied | Re-deploy frontend after changing env var (Vercel bakes it in at build time) |
| Backend sleeps after idle (free tier) | First request after ~15 min idle is slow (~30-60s) while Render wakes it. Judges should use it continuously, or upgrade to paid "always-on" |

---

## Step 6 (optional) — Cloudflare R2 media storage

Without R2, uploaded evidence is stored on the server's local disk (works fine for a demo, but resets on re-deploy).

1. Cloudflare dashboard → **R2** → create bucket `satyakavach-media`.
2. R2 → **Manage R2 API Tokens** → create token → copy **Endpoint**, **Access Key ID**, **Secret Access Key**.
3. Put those into the Render env vars from Step 3.

---

## Updating the app later

Just `git push` to the connected branch:
- Vercel auto-redeploys the frontend.
- Render auto-redeploys the backend.

---

## Quick reference (URLs)

- Frontend (judges use this): `https://<your-app>.vercel.app`
- Backend API: `https://<your-backend>.onrender.com`
- API docs (Swagger): `https://<your-backend>.onrender.com/docs`
- Health check: `https://<your-backend>.onrender.com/health`
