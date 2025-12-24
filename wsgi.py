"""
WSGI entry point untuk PythonAnywhere
File ini digunakan oleh PythonAnywhere untuk menjalankan aplikasi Flask

INSTRUKSI:
1. Copy isi file ini ke WSGI configuration file di PythonAnywhere
2. Ganti 'yourusername' dengan username PythonAnywhere Anda
3. Pastikan path sesuai dengan lokasi project Anda
"""
import sys
import os

# Tambahkan path ke direktori project
# PENTING: Ganti 'yourusername' dengan username PythonAnywhere Anda!
path = '/home/yourusername/scraping-maps'
if path not in sys.path:
    sys.path.insert(0, path)

# Set working directory
os.chdir(path)

# Import aplikasi Flask
from app import app

# PythonAnywhere akan menggunakan variabel 'application'
application = app

