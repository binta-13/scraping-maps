from flask import Flask, render_template, request, jsonify
from scraper import GoogleMapsScraper
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Halaman utama dengan form input"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_maps():
    """API endpoint untuk scraping Google Maps"""
    try:
        data = request.get_json()
        
        # Ambil parameter dari request
        query = data.get('query', '')
        location = data.get('location', '')
        min_rating = float(data.get('min_rating', 0))
        max_results = int(data.get('max_results', 100))
        lat = data.get('lat')
        lng = data.get('lng')
        radius_m = data.get('radius_m')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query harus diisi'
            }), 400
        
        if not location and (not lat or not lng):
            return jsonify({
                'success': False,
                'error': 'Location atau koordinat (lat, lng) harus diisi'
            }), 400
        
        # Parse koordinat jika ada
        lat_float = float(lat) if lat else None
        lng_float = float(lng) if lng else None
        radius_int = int(radius_m) if radius_m else None
        
        # Inisialisasi scraper
        scraper = GoogleMapsScraper()
        
        # Lakukan scraping
        results = scraper.search_places(
            query=query,
            location=location,
            min_rating=min_rating,
            max_results=max_results,
            lat=lat_float,
            lng=lng_float,
            radius_m=radius_int
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
    """Endpoint untuk form submission (HTML form)"""
    try:
        query = request.form.get('query', '')
        location = request.form.get('location', '')
        min_rating = float(request.form.get('min_rating', 0))
        max_results = int(request.form.get('max_results', 100))
        
        # Validasi
        if not query or not location:
            return render_template('index.html', 
                                 error='Query dan location harus diisi')
        
        print(f"[INFO] Memulai scraping: {query} di {location} dengan rating >= {min_rating}, max_results = {max_results}")
        scraper = GoogleMapsScraper()
        results = scraper.search_places(
            query=query,
            location=location,
            min_rating=min_rating,
            max_results=max_results
        )
        
        print(f"[INFO] Scraping selesai. Ditemukan {len(results)} hasil")
        return render_template('index.html', 
                             results=results,
                             query=query,
                             location=location,
                             min_rating=min_rating,
                             max_results=max_results,
                             total=len(results))
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] {error_msg}")
        return render_template('index.html', 
                             error=error_msg,
                             query=request.form.get('query', ''),
                             location=request.form.get('location', ''),
                             min_rating=request.form.get('min_rating', '0'),
                             max_results=request.form.get('max_results', '100'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
