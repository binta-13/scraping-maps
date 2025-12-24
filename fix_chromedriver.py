"""
Script untuk memperbaiki masalah ChromeDriver
Jalankan script ini jika mengalami error WinError 193
"""
import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager

def fix_chromedriver():
    """Membersihkan cache dan install ulang ChromeDriver"""
    print("=" * 50)
    print("Memperbaiki ChromeDriver...")
    print("=" * 50)
    
    # 1. Hapus cache webdriver-manager
    cache_paths = [
        os.path.join(os.path.expanduser("~"), ".wdm"),
        os.path.join(os.path.expanduser("~"), ".cache", "selenium"),
    ]
    
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                print(f"[INFO] Menghapus cache: {cache_path}")
                shutil.rmtree(cache_path, ignore_errors=True)
                print(f"[OK] Cache dihapus: {cache_path}")
            except Exception as e:
                print(f"[GAGAL] Gagal menghapus {cache_path}: {e}")
        else:
            print(f"[INFO] Cache tidak ditemukan: {cache_path}")
    
    # 2. Install ulang ChromeDriver
    try:
        print("\n[INFO] Menginstall ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"[OK] ChromeDriver berhasil diinstall di: {driver_path}")
        return True
    except Exception as e:
        print(f"[GAGAL] Gagal install ChromeDriver: {e}")
        print("\n[SOLUSI]")
        print("1. Pastikan Chrome browser terinstall")
        print("2. Update Chrome ke versi terbaru")
        print("3. Coba jalankan: pip install --upgrade webdriver-manager")
        return False

if __name__ == "__main__":
    success = fix_chromedriver()
    if success:
        print("\n[OK] ChromeDriver sudah diperbaiki. Coba jalankan app.py lagi.")
    else:
        print("\n[GAGAL] ChromeDriver masih bermasalah. Ikuti instruksi di atas.")

