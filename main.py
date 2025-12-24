from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import requests
from urllib.parse import urljoin, urlparse
import mimetypes

# ========== Setup Selenium ==========
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
url = "https://www.jogjaworldheritage.com/id/livingheritage/batik"
driver.get(url)

# Tunggu sampai konten utama muncul
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
time.sleep(3)

# ========== Ambil semua konten teks unik ==========
text_set = set()

# Dari elemen h1, h2, p
for tag in ["h1", "h2", "p"]:
    for el in driver.find_elements(By.TAG_NAME, tag):
        text = el.text.strip()
        if text:
            text_set.add(text)

# Dari div utama (jika ada konten innerText yang unik)
for el in driver.find_elements(By.CSS_SELECTOR, "div[data-testid='SITE_PAGES']"):
    text = el.get_attribute("innerText").strip()
    if text:
        text_set.add(text)

# Simpan ke file
with open("konten_website_filosofi_kraton.txt", "w", encoding="utf-8") as f:
    f.write("=== KONTEN TEKS UNIK ===\n\n")
    for t in sorted(text_set):
        f.write(t + "\n\n")
print("✅ Teks unik disimpan ke: konten_website_filosofi_kraton.txt")

# ========== Simpan isi dari satu <div> pertama yang memiliki teks ==========
div_elements = driver.find_elements(By.TAG_NAME, "div")
for idx, div in enumerate(div_elements):
    div_text = div.text.strip()
    if div_text:
        with open("div_pertama_filosofi_kraton.txt", "w", encoding="utf-8") as f:
            f.write(f"[DIV {idx+1}]\n{div_text}\n")
        print("✅ Isi <div> pertama yang punya teks disimpan ke: div_pertama_filosofi_kraton.txt")
        break

# ========== Download semua gambar ==========
img_dir = "images-batik"
os.makedirs(img_dir, exist_ok=True)

img_elements = driver.find_elements(By.TAG_NAME, "img")
for i, img in enumerate(img_elements):
    src = img.get_attribute("src") or img.get_attribute("srcset") or img.get_attribute("data-src")
    if src and not src.startswith("data:"):
        img_url = urljoin(url, src)
        try:
            parsed_url = urlparse(img_url)
            ext = os.path.splitext(parsed_url.path)[1]
            ext = ext if ext else ".jpg"
            filename = os.path.join(img_dir, f"image_{i+1}{ext}")

            img_data = requests.get(img_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"[GAMBAR] {img_url} -> {filename}")
        except Exception as e:
            print(f"[GAGAL] {img_url} - {e}")

# ========== Ambil semua link file (.pdf, .doc, .zip) ==========
print("\n=== LINK FILE TERDETEKSI ===\n")
for a in driver.find_elements(By.TAG_NAME, "a"):
    href = a.get_attribute("href")
    if href and any(href.lower().endswith(ext) for ext in [".pdf", ".doc", ".zip"]):
        print(href)

# ========== Selesai ==========
driver.quit()
print("\n✅ Semua proses selesai.")
