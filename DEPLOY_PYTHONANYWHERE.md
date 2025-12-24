# Panduan Deploy ke PythonAnywhere

PythonAnywhere adalah platform yang sangat cocok untuk aplikasi Flask dengan Selenium karena:
- ✅ **Gratis** untuk aplikasi web (dengan beberapa batasan)
- ✅ **Support Selenium** dengan Chrome/ChromeDriver
- ✅ **Python environment lengkap**
- ✅ **Tidak ada timeout** untuk request (kecuali batasan CPU)
- ✅ **SSH access** untuk debugging

## Langkah 1: Daftar di PythonAnywhere

1. Kunjungi [pythonanywhere.com](https://www.pythonanywhere.com)
2. Klik "Beginner: sign up for a free account"
3. Buat akun baru (gratis)

## Langkah 2: Upload Code ke PythonAnywhere

### Metode 1: Via GitHub (Rekomendasi)

1. **Push code ke GitHub** (jika belum):
   ```bash
   git add .
   git commit -m "Setup for PythonAnywhere"
   git push origin main
   ```

2. **Di PythonAnywhere Dashboard**:
   - Buka tab **Files**
   - Klik **"Open Bash console here"**
   - Clone repository:
     ```bash
     git clone https://github.com/username/your-repo.git scraping-maps
     cd scraping-maps
     ```

### Metode 2: Via Upload Manual

1. **Di PythonAnywhere Dashboard**:
   - Buka tab **Files**
   - Buat folder baru: `scraping-maps`
   - Upload semua file project (app.py, scraper.py, templates/, requirements.txt, dll)

## Langkah 3: Setup Python Environment

1. **Buka Bash console** di PythonAnywhere

2. **Install dependencies**:
   ```bash
   cd ~/scraping-maps
   pip3.10 install --user -r requirements.txt
   ```
   
   **Catatan**: PythonAnywhere menggunakan Python 3.10, jadi gunakan `pip3.10`

3. **Verifikasi instalasi**:
   ```bash
   python3.10 -c "import flask; import selenium; print('OK')"
   ```

## Langkah 4: Konfigurasi WSGI

1. **Di PythonAnywhere Dashboard**, buka tab **Web**

2. **Klik "Add a new web app"** (jika belum ada)

3. **Pilih domain**:
   - Free account: `yourusername.pythonanywhere.com`
   - Paid account: bisa menggunakan custom domain

4. **Pilih Python version**: Python 3.10

5. **Klik "Next"** sampai selesai

6. **Edit WSGI configuration file**:
   - Klik link **"WSGI configuration file"**
   - Hapus semua isi file
   - Copy paste isi dari `wsgi.py` di project Anda
   - **PENTING**: Ganti `yourusername` dengan username PythonAnywhere Anda
   - Contoh:
     ```python
     import sys
     import os
     
     path = '/home/yourusername/scraping-maps'  # Ganti yourusername!
     if path not in sys.path:
         sys.path.insert(0, path)
     
     from app import app
     application = app
     ```

7. **Save file**

## Langkah 5: Setup Static Files (Opsional)

Jika ada file static (CSS, JS, images):

1. Di tab **Web**, scroll ke **Static files**
2. **URL**: `/static/`
3. **Directory**: `/home/yourusername/scraping-maps/static`

## Langkah 6: Reload Web App

1. Di tab **Web**, scroll ke bawah
2. Klik tombol **"Reload yourusername.pythonanywhere.com"**
3. Tunggu beberapa detik

## Langkah 7: Test Aplikasi

1. Buka browser dan akses: `https://yourusername.pythonanywhere.com`
2. Seharusnya halaman form muncul
3. Test dengan melakukan pencarian

## Troubleshooting

### Error: Module not found

**Solusi**:
```bash
# Di Bash console
cd ~/scraping-maps
pip3.10 install --user -r requirements.txt
```

### Error: ChromeDriver tidak ditemukan

**Solusi**: 
- `webdriver-manager` seharusnya otomatis download ChromeDriver
- Jika masih error, cek di **Tasks** tab apakah ada error log

### Error: Template tidak ditemukan

**Solusi**:
- Pastikan folder `templates/` ada di direktori project
- Pastikan path di `wsgi.py` benar

### Error: 500 Internal Server Error

**Solusi**:
1. Buka tab **Web** → **Error log**
2. Lihat error message
3. Perbaiki sesuai error

### Aplikasi tidak reload

**Solusi**:
- Pastikan sudah klik **"Reload"** di tab Web
- Tunggu 10-30 detik
- Clear browser cache

## Konfigurasi Lanjutan

### Custom Domain (Paid Account)

1. Di tab **Web**, scroll ke **Domains**
2. Tambahkan custom domain
3. Setup DNS sesuai instruksi PythonAnywhere

### Scheduled Tasks (Cron Jobs)

1. Buka tab **Tasks**
2. Tambahkan scheduled task
3. Contoh: backup data setiap hari

### Database (Jika Diperlukan)

1. Buka tab **Databases**
2. Buat MySQL database (free account: 1 database)
3. Update kode untuk menggunakan database

## Batasan Free Account

- ✅ 1 web app
- ✅ 1 MySQL database
- ✅ 512 MB disk space
- ✅ CPU limit: 100 detik per hari
- ⚠️ Website sleep setelah 3 bulan tidak aktif (bisa dibangunkan dengan klik)

## Upgrade ke Paid Account

Jika perlu lebih banyak resources:
- **Hacker plan**: $5/bulan
- **Web Developer plan**: $12/bulan
- **Custom plan**: Contact support

## Tips

1. **Gunakan Git**: Lebih mudah untuk update code
2. **Monitor Error Log**: Cek error log secara berkala
3. **Test Lokal Dulu**: Pastikan aplikasi bekerja di local sebelum deploy
4. **Backup**: Backup code dan database secara berkala

## Support

Jika ada masalah:
- [PythonAnywhere Help](https://help.pythonanywhere.com)
- [PythonAnywhere Forum](https://www.pythonanywhere.com/forums/)

