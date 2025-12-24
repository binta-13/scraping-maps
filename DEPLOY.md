# Panduan Deploy ke Netlify

## ⚠️ Peringatan Penting

Aplikasi ini menggunakan **Selenium dengan ChromeDriver** yang memiliki beberapa tantangan untuk deploy di Netlify:

1. **Timeout Limit**: Netlify Functions memiliki batasan timeout:
   - Free plan: 10 detik
   - Pro plan: 10 detik
   - Pro+ plan: 26 detik
   
   Scraping Google Maps bisa memakan waktu lebih dari 10 detik, terutama untuk banyak hasil.

2. **Chrome/ChromeDriver**: Netlify Functions mungkin tidak memiliki Chrome browser yang diperlukan untuk Selenium.

3. **Memory Limit**: Netlify Functions memiliki batasan memory yang mungkin tidak cukup untuk Selenium.

## Rekomendasi Platform Alternatif

Untuk aplikasi dengan Selenium, pertimbangkan platform berikut:

### 1. Railway (Rekomendasi)
- ✅ Mudah setup
- ✅ Support Python dengan Selenium
- ✅ Free tier tersedia
- ✅ Auto-deploy dari GitHub

**Setup Railway**:
1. Sign up di [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Pilih repository
4. Railway akan auto-detect Flask app
5. Add environment variables jika diperlukan

### 2. Render
- ✅ Free tier tersedia
- ✅ Support Python
- ✅ Auto-deploy dari GitHub

**Setup Render**:
1. Sign up di [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`

### 3. PythonAnywhere
- ✅ Gratis untuk aplikasi web
- ✅ Support Selenium
- ✅ Python environment lengkap

## Deploy ke Netlify (Jika Tetap Ingin Mencoba)

### Metode 1: Via Netlify CLI

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Login:
```bash
netlify login
```

3. Initialize project:
```bash
netlify init
```

4. Deploy:
```bash
netlify deploy --prod
```

### Metode 2: Via GitHub

1. Push code ke GitHub:
```bash
git add .
git commit -m "Setup for Netlify"
git push origin main
```

2. Login ke [Netlify Dashboard](https://app.netlify.com)

3. Klik "New site from Git"

4. Pilih GitHub dan repository

5. Build settings:
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`

6. Klik "Deploy site"

### Troubleshooting

Jika mengalami error:

1. **Timeout Error**: 
   - Upgrade ke Pro+ plan (26 detik timeout)
   - Atau kurangi `max_results` di scraping

2. **ChromeDriver Error**:
   - Netlify mungkin tidak support Chrome
   - Pertimbangkan platform alternatif

3. **Memory Error**:
   - Upgrade plan untuk lebih banyak memory
   - Atau optimasi kode scraping

## Testing Lokal dengan Netlify Dev

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Jalankan local development:
```bash
netlify dev
```

Ini akan menjalankan Netlify Functions secara lokal untuk testing.

## Catatan

Jika deploy ke Netlify tidak berhasil karena batasan Selenium, sangat disarankan untuk menggunakan Railway atau Render yang lebih cocok untuk aplikasi Python dengan Selenium.

