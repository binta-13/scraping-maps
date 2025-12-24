# Google Maps Scraper

Aplikasi web untuk scraping data tempat dari Google Maps menggunakan Flask dan Selenium.

## Fitur

- Scraping data tempat dari Google Maps
- Filter berdasarkan rating minimum
- Dukungan pencarian dengan lokasi atau koordinat
- Web interface yang user-friendly
- API endpoint untuk integrasi

## Setup Lokal

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
python app.py
```

3. Buka browser di `http://localhost:5000`

## Deploy ke Netlify

### Catatan Penting

⚠️ **Peringatan**: Aplikasi ini menggunakan Selenium dengan ChromeDriver yang memerlukan:
- Chrome browser terinstall
- Waktu eksekusi yang cukup lama (bisa > 10 detik)

Netlify Functions memiliki batasan:
- Free plan: 10 detik timeout
- Pro plan: 10 detik timeout  
- Pro+ plan: 26 detik timeout

**Rekomendasi**: Untuk aplikasi dengan Selenium, pertimbangkan platform lain seperti:
- Railway
- Render
- Heroku
- PythonAnywhere

### Langkah Deploy

1. **Install Netlify CLI** (opsional):
```bash
npm install -g netlify-cli
```

2. **Login ke Netlify**:
```bash
netlify login
```

3. **Deploy**:
```bash
netlify deploy --prod
```

Atau melalui GitHub:
1. Push code ke GitHub
2. Login ke [Netlify](https://app.netlify.com)
3. Pilih "New site from Git"
4. Pilih repository
5. Build settings:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `public`
6. Deploy

### Konfigurasi Environment Variables

Jika diperlukan, tambahkan environment variables di Netlify dashboard:
- Settings → Environment variables

## Struktur Project

```
.
├── app.py                 # Flask application
├── scraper.py             # Google Maps scraper
├── requirements.txt       # Python dependencies
├── netlify.toml          # Netlify configuration
├── netlify/
│   └── functions/
│       └── server.py     # Netlify serverless function
└── templates/
    └── index.html        # Web interface
```

## API Endpoints

### POST /api/scrape
API endpoint untuk scraping (JSON)

**Request Body**:
```json
{
  "query": "hotel",
  "location": "Yogyakarta",
  "min_rating": 4.0,
  "max_results": 100
}
```

### POST /api/scrape-form
Endpoint untuk form submission (HTML form)

## License

MIT

