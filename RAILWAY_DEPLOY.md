# Apres Radar Scraper - Railway Deployment Guide

## 🚀 Deploy to Railway (10 Minutes)

### Step 1: Upload Files to GitHub

1. Go to your GitHub repo: `https://github.com/brodyjamesmcdonald/apres-radar`
2. Click **"Add file"** → **"Create new file"**
3. Name it: `scraper/main.py`
4. Copy/paste the content from `main.py`
5. Click **"Commit changes"**
6. Repeat for other files:
   - `scraper/resort_scrapers.py`
   - `scraper/requirements.txt`
   - `scraper/railway.toml`

**OR** create a `scraper` folder and upload all 4 files at once.

---

### Step 2: Deploy to Railway

1. Go to Railway dashboard: https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **"apres-radar"** repository
5. Railway will detect your Python app automatically
6. Click **"Deploy"**

---

### Step 3: Add Environment Variables (CRITICAL!)

1. In Railway, click on your deployed project
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add these 3 variables:

**Variable 1:**
- Name: `SUPABASE_URL`
- Value: `https://pofptakbbdrmkjybmhbm.supabase.co`

**Variable 2:**
- Name: `SUPABASE_KEY`
- Value: [Paste your Supabase secret key here - the long sb_secret_... string]

**Variable 3:**
- Name: `TZ`
- Value: `America/Denver`

4. Click **"Save"** or Railway auto-saves

---

### Step 4: Set Up Daily Schedule

Railway doesn't have built-in cron, so we need to use **Railway Cron** plugin:

1. In your project, click **"New"** → **"Plugin"**
2. Search for **"Cron"** or use GitHub Actions
3. Set schedule: `0 6 * * *` (6am daily Mountain Time)

**OR** use GitHub Actions (preferred):

Create `.github/workflows/daily-scraper.yml` in your repo:

```yaml
name: Daily Event Scraper

on:
  schedule:
    - cron: '0 13 * * *'  # 6am MT = 1pm UTC
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd scraper
          pip install -r requirements.txt
      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          cd scraper
          python main.py
```

Then add secrets in GitHub:
- Settings → Secrets → Actions → New repository secret
- Add `SUPABASE_URL` and `SUPABASE_KEY`

---

### Step 5: Test It!

**Manual Test:**
1. In Railway, go to your project
2. Click **"Deployments"**
3. Click **"Deploy"** to trigger manually
4. Check **"Logs"** tab to see output
5. You should see: "✅ Copper Mountain: X events saved"

**Check Supabase:**
1. Go to Supabase → Table Editor → `events`
2. You should see real events populated!

---

## 🐛 Troubleshooting

**No events scraped?**
- Websites may have changed structure
- Check Railway logs for errors
- We'll debug specific scrapers in next session

**Deployment failed?**
- Check Railway logs
- Make sure all files are uploaded
- Verify environment variables are set

**Can't connect to Supabase?**
- Double-check SUPABASE_URL and SUPABASE_KEY
- Make sure you're using the SECRET key, not publishable

---

## ✅ Success Checklist

- [ ] Files uploaded to GitHub `scraper/` folder
- [ ] Deployed to Railway
- [ ] Environment variables added
- [ ] Test deployment successful
- [ ] Events appear in Supabase
- [ ] Daily schedule configured

---

## 📊 What Happens Daily

Every day at 6am MT:
1. Scraper runs on Railway
2. Visits all 12 resort websites
3. Extracts events through end of season
4. Saves to Supabase database
5. Cleans up old events (30+ days past)
6. Logs summary

Your website will automatically show new events!
