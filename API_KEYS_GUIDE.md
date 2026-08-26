# 🔑 API Keys Setup Guide — SatyaKavach

## Quick Summary

| API | Needed For | Free Tier | Required? |
|-----|-----------|-----------|-----------|
| **Gemini API** | AI reasoning + vision | ✅ Free (generous) | ⭐ Recommended |
| **VirusTotal** | URL/file reputation | ✅ Free (4 req/min) | Optional |
| **Google Safe Browsing** | Malicious URL detection | ✅ Free (10K/day) | Optional |
| **PhishTank** | Phishing URL database | ✅ Free (open data) | Optional |

> **💡 Good news:** Everything works in **DEMO MODE** without any API keys! The app uses realistic mock data by default. Add API keys when you want live results.

---

## 1. Google Gemini API (Recommended)

**What it does:** Powers the AI reasoning layer — generates evidence reports, explains verdicts, analyzes images with vision.

### How to get it (FREE):

1. Go to **https://ai.google.dev**
2. Click **"Get API Key"** or **"Get started"**
3. Sign in with your Google account
4. In Google AI Studio, click **"Get API key"** in the left sidebar
5. Click **"Create API key"**
6. Copy the key (looks like `AIzaSy...`)

### Free tier limits:
- **Gemini 2.0 Flash** — completely free for input & output tokens
- Enough for thousands of verification requests
- No credit card required

### Add to `.env`:
```
GEMINI_API_KEY=AIzaSyYourKeyHere
```

---

## 2. VirusTotal API (Optional)

**What it does:** Scans uploaded files and URLs against 70+ antivirus engines for malware/phishing detection.

### How to get it (FREE):

1. Go to **https://www.virustotal.com**
2. Create a free account
3. Go to **https://www.virustotal.com/gui/my-apikey**
4. Copy your API key

### Free tier limits:
- **4 requests/minute**
- 500 requests/day
- For demo: adequate (we cache results)

### Add to `.env`:
```
VIRUSTOTAL_API_KEY=your-virustotal-api-key
```

---

## 3. Google Safe Browsing API (Optional)

**What it does:** Checks URLs against Google's database of known malicious sites (phishing, malware, unwanted software).

### How to get it (FREE):

1. Go to **https://console.cloud.google.com**
2. Create a project (or use existing)
3. Enable the **"Safe Browsing API"**:
   - Go to APIs & Services → Library
   - Search "Safe Browsing"
   - Click "Enable"
4. Go to **APIs & Services → Credentials**
5. Click **"Create Credentials" → "API Key"**
6. Copy the key

### Free tier limits:
- **10,000 queries/day** (Lookup API)
- More than enough for demo and pilot

### Add to `.env`:
```
GOOGLE_SAFE_BROWSING_API_KEY=your-google-api-key
```

---

## 4. PhishTank (Optional)

**What it does:** Checks URLs against a community-maintained database of known phishing sites.

### How to get it (FREE):

1. Go to **https://phishtank.org**
2. Create a free account
3. Go to **https://phishtank.org/developer_info.php**
4. Register your application
5. Copy your application key

### Free tier limits:
- Free for non-commercial use
- Hourly updated phishing database

### Add to `.env`:
```
PHISHTANK_APP_KEY=your-phishtank-key
```

---

## Complete `.env` file

```bash
# ── Application ──
DEMO_MODE=true          # Set to false when you have API keys
DEBUG=true

# ── Database ──
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/satya

# ── Storage ──
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# ── Redis ──
REDIS_URL=redis://redis:6379/0

# ── JWT ──
JWT_SECRET_KEY=your-super-secret-random-string-here

# ── API Keys (get free keys from links above) ──
GEMINI_API_KEY=AIzaSy...
VIRUSTOTAL_API_KEY=your-key
GOOGLE_SAFE_BROWSING_API_KEY=your-key
PHISHTANK_APP_KEY=your-key
```

---

## Minimum Setup for Demo

**You only need 0 API keys to run the demo!** Just:

1. Set `DEMO_MODE=true` (default)
2. Run `docker-compose up`
3. Open http://localhost:3000
4. Upload any file → you'll get realistic demo results

**For a better demo**, add the **Gemini API key** — it's free and gives you real AI-powered evidence reports.

---

## Switching from Demo to Live

```bash
# 1. Get your API keys (see above)

# 2. Update .env
DEMO_MODE=false
GEMINI_API_KEY=AIzaSyYourKey
VIRUSTOTAL_API_KEY=your-key
GOOGLE_SAFE_BROWSING_API_KEY=your-key

# 3. Restart
docker-compose down && docker-compose up --build
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "API key not configured" | Add the key to `.env` and restart |
| VirusTotal 429 error | Rate limited — wait 15 seconds, we cache results |
| Gemini timeout | Check API key is valid at ai.google.dev |
| PhishTank no data | Normal for rare URLs — falls back to domain heuristics |
