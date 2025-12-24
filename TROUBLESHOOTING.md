# Troubleshooting Netlify Deployment

## Error 404 - Page Not Found

Jika Anda mendapatkan error 404, berikut langkah troubleshooting:

### 1. Periksa Struktur Function

Pastikan struktur folder benar:
```
netlify/
  functions/
    server/
      server.py
      requirements.txt
```

### 2. Periksa Logs di Netlify

1. Buka Netlify Dashboard
2. Pilih site Anda
3. Klik "Functions" tab
4. Lihat logs untuk error messages

### 3. Test Function Langsung

Coba akses function langsung:
- `https://your-site.netlify.app/.netlify/functions/server`

Jika ini bekerja, masalahnya di redirect. Jika tidak, masalahnya di function.

### 4. Periksa Redirect di netlify.toml

Pastikan redirect mengarah ke function yang benar:
```toml
[[redirects]]
  from = "/*"
  to = "/.netlify/functions/server"
  status = 200
```

### 5. Periksa Build Logs

1. Buka Netlify Dashboard
2. Pilih site
3. Klik "Deploys" tab
4. Lihat build logs untuk error

### 6. Common Issues

#### Issue: Function tidak terdeteksi
**Solusi**: Pastikan file `server.py` ada di `netlify/functions/server/`

#### Issue: Import error
**Solusi**: Pastikan `requirements.txt` ada di `netlify/functions/server/` dan semua dependencies terinstall

#### Issue: Path error
**Solusi**: Periksa path di `server.py` - harus menggunakan `../../..` untuk naik ke root

#### Issue: Template tidak ditemukan
**Solusi**: Pastikan `templates/` folder ada dan di-include di `netlify.toml`:
```toml
[functions]
  included_files = ["templates/**", "scraper.py", "app.py"]
```

### 7. Debug Mode

Tambahkan logging di `server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 8. Test Lokal dengan Netlify Dev

```bash
npm install -g netlify-cli
netlify dev
```

Ini akan menjalankan function secara lokal untuk testing.

## Masalah Selenium/ChromeDriver

Jika function berjalan tapi scraping gagal:

1. **Chrome tidak tersedia**: Netlify Functions mungkin tidak memiliki Chrome browser
2. **Timeout**: Scraping memakan waktu > 10 detik (limit Netlify)
3. **Memory**: Selenium memerlukan banyak memory

**Solusi**: Pertimbangkan platform alternatif seperti Railway atau Render yang lebih cocok untuk Selenium.

