import os

# Buat folder templates
os.makedirs('templates', exist_ok=True)

# 1. File app.py
app_py = """from flask import Flask, render_template, request, jsonify
from scraper import GoogleMapsScraper
import os

app = Flask(__name__)

@app.route('/')
def index():
    \"\"\"Halaman utama dengan form input\"\"\"
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_maps():
    \"\"\"API endpoint untuk scraping Google Maps\"\"\"
    try:
        data = request.get_json()
        
        # Ambil parameter dari request
        query = data.get('query', '')
        location = data.get('location', '')
        min_rating = float(data.get('min_rating', 0))
        
        if not query or not location:
            return jsonify({
                'success': False,
                'error': 'Query dan location harus diisi'
            }), 400
        
        # Inisialisasi scraper
        scraper = GoogleMapsScraper()
        
        # Lakukan scraping
        results = scraper.search_places(
            query=query,
            location=location,
            min_rating=min_rating
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'location': location,
            'min_rating': min_rating,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape-form', methods=['POST'])
def scrape_maps_form():
    \"\"\"Endpoint untuk form submission (HTML form)\"\"\"
    try:
        query = request.form.get('query', '')
        location = request.form.get('location', '')
        min_rating = float(request.form.get('min_rating', 0))
        
        if not query or not location:
            return render_template('index.html', 
                                 error='Query dan location harus diisi')
        
        scraper = GoogleMapsScraper()
        results = scraper.search_places(
            query=query,
            location=location,
            min_rating=min_rating
        )
        
        return render_template('index.html', 
                             results=results,
                             query=query,
                             location=location,
                             min_rating=min_rating,
                             total=len(results))
        
    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""

# 2. File scraper.py
scraper_py = """from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

class GoogleMapsScraper:
    def __init__(self, headless=True):
        \"\"\"Inisialisasi scraper dengan Selenium\"\"\"
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
    def _get_driver(self):
        \"\"\"Membuat driver Chrome\"\"\"
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=self.options
        )
    
    def search_places(self, query, location, min_rating=0, max_results=20):
        \"\"\"
        Mencari tempat di Google Maps
        
        Args:
            query: Kata kunci pencarian (contoh: "kedai kopi")
            location: Lokasi (contoh: "Jogja" atau "Yogyakarta")
            min_rating: Rating minimum (contoh: 4.0)
            max_results: Maksimal hasil yang diambil
        
        Returns:
            List of dict dengan informasi tempat
        \"\"\"
        driver = None
        try:
            driver = self._get_driver()
            wait = WebDriverWait(driver, 20)
            
            # Buka Google Maps
            search_query = f"{query} {location}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            driver.get(url)
            
            # Tunggu hasil muncul
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(5)
            
            # Scroll untuk memuat lebih banyak hasil
            self._scroll_results(driver, max_results)
            
            # Ambil semua hasil
            results = []
            place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            for element in place_elements[:max_results]:
                try:
                    place_data = self._extract_place_info(element, min_rating)
                    if place_data:
                        results.append(place_data)
                except Exception as e:
                    print(f"[GAGAL] Error extracting place info: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"[GAGAL] Error during scraping: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def _scroll_results(self, driver, max_results):
        \"\"\"Scroll sidebar untuk memuat lebih banyak hasil\"\"\"
        try:
            # Temukan sidebar hasil
            sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            
            # Scroll beberapa kali untuk memuat lebih banyak hasil
            scroll_count = max(1, max_results // 10)
            for _ in range(scroll_count):
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    sidebar
                )
                time.sleep(2)
        except Exception as e:
            print(f"[GAGAL] Error scrolling: {e}")
    
    def _extract_place_info(self, element, min_rating):
        \"\"\"Ekstrak informasi dari elemen tempat\"\"\"
        try:
            # Nama tempat
            name_elem = element.find_elements(By.CSS_SELECTOR, "div[data-value='Name']")
            name = name_elem[0].text if name_elem else "N/A"
            
            # Rating
            rating_elem = element.find_elements(By.CSS_SELECTOR, "span[aria-label*='Bintang']")
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem[0].get_attribute("aria-label")
                rating_match = re.search(r'(\\d+[.,]\\d+|\\d+)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1).replace(',', '.'))
            
            # Filter berdasarkan rating minimum
            if rating < min_rating:
                return None
            
            # Jumlah review
            review_elem = element.find_elements(By.CSS_SELECTOR, "span[aria-label*='review']")
            review_count = 0
            if review_elem:
                review_text = review_elem[0].get_attribute("aria-label")
                review_match = re.search(r'(\\d+)', review_text.replace(',', '').replace('.', ''))
                if review_match:
                    review_count = int(review_match.group(1))
            
            # Kategori/Tipe
            category_elem = element.find_elements(By.CSS_SELECTOR, "div[data-value='Category']")
            category = category_elem[0].text if category_elem else "N/A"
            
            # Alamat
            address_elem = element.find_elements(By.CSS_SELECTOR, "div[data-value='Address']")
            address = address_elem[0].text if address_elem else "N/A"
            
            # Link
            link_elem = element.find_elements(By.CSS_SELECTOR, "a[data-value='Directions']")
            link = link_elem[0].get_attribute("href") if link_elem else ""
            
            return {
                'name': name,
                'rating': rating,
                'review_count': review_count,
                'category': category,
                'address': address,
                'link': link
            }
            
        except Exception as e:
            print(f"[GAGAL] Error extracting place info: {e}")
            return None
"""

# 3. File requirements.txt
requirements_txt = """Flask==3.0.0
selenium==4.15.2
webdriver-manager==4.0.1
requests==2.31.0
"""

# 4. File templates/index.html
index_html = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Maps Scraper</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .form-container {
            padding: 40px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        
        input[type="text"],
        input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus,
        input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .results-container {
            padding: 40px;
            display: none;
        }
        
        .results-container.show {
            display: block;
        }
        
        .summary {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .summary h2 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .result-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        .result-card h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .rating {
            display: inline-block;
            background: #ffc107;
            color: #333;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .info {
            color: #666;
            margin: 5px 0;
            font-size: 0.9em;
        }
        
        .error {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ Google Maps Scraper</h1>
            <p>Scraping data tempat dari Google Maps secara dinamis</p>
        </div>
        
        <div class="form-container">
            <form id="scrapeForm" method="POST" action="/api/scrape-form">
                <div class="form-group">
                    <label for="query">Kata Kunci Pencarian:</label>
                    <input type="text" id="query" name="query" 
                           placeholder="Contoh: kedai kopi, restoran, hotel" 
                           value="{{ query if query else '' }}" required>
                </div>
                
                <div class="form-group">
                    <label for="location">Lokasi:</label>
                    <input type="text" id="location" name="location" 
                           placeholder="Contoh: Jogja, Yogyakarta, Jakarta" 
                           value="{{ location if location else '' }}" required>
                </div>
                
                <div class="form-group">
                    <label for="min_rating">Rating Minimum:</label>
                    <input type="number" id="min_rating" name="min_rating" 
                           step="0.1" min="0" max="5" 
                           value="{{ min_rating if min_rating else 0 }}" required>
                </div>
                
                <button type="submit" class="btn">🔍 Mulai Scraping</button>
            </form>
            
            {% if error %}
            <div class="error">
                <strong>Error:</strong> {{ error }}
            </div>
            {% endif %}
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Sedang melakukan scraping... Mohon tunggu</p>
            </div>
        </div>
        
        {% if results %}
        <div class="results-container show">
            <div class="summary">
                <h2>📊 Hasil Pencarian</h2>
                <p>Ditemukan <strong>{{ total }}</strong> tempat dengan rating ≥ {{ min_rating }}</p>
                <p><strong>Query:</strong> {{ query }} di {{ location }}</p>
            </div>
            
            <div class="results-grid">
                {% for result in results %}
                <div class="result-card">
                    <h3>{{ result.name }}</h3>
                    <div class="rating">⭐ {{ result.rating }} / 5.0</div>
                    <div class="info">📝 {{ result.review_count }} review</div>
                    <div class="info">🏷️ {{ result.category }}</div>
                    <div class="info">📍 {{ result.address }}</div>
                    {% if result.link %}
                    <div class="info">
                        <a href="{{ result.link }}" target="_blank">Lihat di Maps →</a>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
    
    <script>
        document.getElementById('scrapeForm').addEventListener('submit', function() {
            document.getElementById('loading').classList.add('show');
        });
    </script>
</body>
</html>
"""

# Tulis semua file
files = {
    'app.py': app_py,
    'scraper.py': scraper_py,
    'requirements.txt': requirements_txt,
    'templates/index.html': index_html
}

print("Membuat folder dan file...")
for filepath, content in files.items():
    # Buat folder jika diperlukan
    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    
    # Tulis file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Dibuat: {filepath}")

print("\n✅ Semua file berhasil dibuat!")
print("\nLangkah selanjutnya:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Jalankan aplikasi: python app.py")
print("3. Buka browser: http://localhost:5000")