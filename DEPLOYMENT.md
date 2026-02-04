# Apres Radar - Deployment Guide

## 🚀 Quick Deploy to Vercel (5 Minutes)

### Method 1: Drag & Drop (Easiest)

1. **Go to Vercel**: https://vercel.com
2. **Sign up** with GitHub (it's free, no credit card needed)
3. Click **"Add New"** → **"Project"**
4. Click **"Browse"** and select the `index.html` file from this folder
5. Click **"Deploy"**
6. **Done!** You'll get a live URL like: `apresradar.vercel.app`

### Method 2: GitHub (Recommended for Updates)

1. **Create GitHub account** if you don't have one: https://github.com
2. **Create new repository**: 
   - Click "+" → "New repository"
   - Name it "apres-radar"
   - Make it Public
   - Click "Create repository"

3. **Upload files**:
   - Click "uploading an existing file"
   - Drag `index.html` into the browser
   - Click "Commit changes"

4. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Sign in with GitHub
   - Click "Add New" → "Project"
   - Select your "apres-radar" repository
   - Click "Deploy"
   - **Done!**

---

## 🎯 After Deployment

You'll get a URL like: `https://apresradar.vercel.app`

### Customize Your Domain (Optional)

**Free Vercel domain:**
- Go to Project Settings → Domains
- Change `apresradar.vercel.app` to whatever you want (if available)

**Custom domain ($12/year):**
- Buy domain at Namecheap/GoDaddy (e.g., `apresradar.com`)
- In Vercel: Project Settings → Domains → Add
- Follow Vercel's instructions to connect

---

## ✅ What You Have Live Now

- ✅ Full website with festival design
- ✅ 16 sample events from Colorado/Utah/California resorts
- ✅ Working filters (Home Base, Weekend, Pass)
- ✅ Email signup form (saves to browser for now)
- ✅ Mobile responsive

---

## 🔄 Next Steps (After Website is Live)

### Step 2: Get Real Scraper Working
- Set up Railway or DigitalOcean server
- Run Python scraper against live resort websites
- Get actual event data

### Step 3: Connect Database
- Set up Supabase (free) to store events
- Replace mock data with live scraped data

### Step 4: Add Email/SMS System
- SendGrid for emails (free tier: 100/day)
- Twilio for SMS (pay-as-you-go)
- Connect signup form to actually save emails

### Step 5: Automate Weekly Radar
- Schedule scraper to run daily
- Send Thursday email with weekend picks
- SMS alerts for major events

---

## 📞 Need Help?

If you get stuck:
1. Check Vercel's documentation: https://vercel.com/docs
2. Most common issue: Make sure file is named `index.html` (not `index.htm`)
3. Deployment takes 30-60 seconds - be patient!

---

## 🎉 You're Live!

Once deployed, share your URL and get feedback. The site works perfectly with sample data while we build the real backend.
