from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import os
import shutil

class GoogleMapsScraper:
    def __init__(self, headless=True):
        """Inisialisasi scraper dengan Selenium"""
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
        """Membuat driver Chrome dengan error handling yang lebih baik"""
        try:
            # Coba dengan ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            
            # Pastikan path adalah file executable, bukan file lain
            if not driver_path.endswith('.exe') and os.path.isdir(driver_path):
                # Cari chromedriver.exe di dalam folder
                for root, dirs, files in os.walk(driver_path):
                    for file in files:
                        if file == 'chromedriver.exe':
                            driver_path = os.path.join(root, file)
                            break
                    if driver_path.endswith('.exe'):
                        break
            
            # Jika masih bukan .exe, coba cari di parent directory
            if not driver_path.endswith('.exe'):
                parent_dir = os.path.dirname(driver_path) if os.path.isfile(driver_path) else driver_path
                exe_path = os.path.join(parent_dir, 'chromedriver.exe')
                if os.path.exists(exe_path):
                    driver_path = exe_path
            
            service = Service(driver_path)
            return webdriver.Chrome(service=service, options=self.options)
        except Exception as e:
            print(f"[GAGAL] Error dengan ChromeDriverManager: {e}")
            # Fallback: coba tanpa service (gunakan Chrome yang sudah terinstall)
            try:
                print("[INFO] Mencoba menggunakan Chrome yang sudah terinstall...")
                return webdriver.Chrome(options=self.options)
            except Exception as e2:
                print(f"[GAGAL] Error membuat driver: {e2}")
                # Coba bersihkan cache dan install ulang
                try:
                    cache_path = os.path.join(os.path.expanduser("~"), ".wdm")
                    if os.path.exists(cache_path):
                        print("[INFO] Membersihkan cache ChromeDriver...")
                        shutil.rmtree(cache_path, ignore_errors=True)
                    driver_path = ChromeDriverManager().install()
                    
                    # Cari chromedriver.exe
                    if not driver_path.endswith('.exe'):
                        for root, dirs, files in os.walk(driver_path if os.path.isdir(driver_path) else os.path.dirname(driver_path)):
                            for file in files:
                                if file == 'chromedriver.exe':
                                    driver_path = os.path.join(root, file)
                                    break
                            if driver_path.endswith('.exe'):
                                break
                    
                    service = Service(driver_path)
                    return webdriver.Chrome(service=service, options=self.options)
                except Exception as e3:
                    print(f"[GAGAL] Semua metode gagal: {e3}")
                    raise Exception(f"Tidak dapat membuat Chrome driver. Pastikan Chrome browser terinstall. Error: {e3}")
    
    def search_places(self, query, location, min_rating=0, max_results=100, lat=None, lng=None, radius_m=None):
        """
        Mencari tempat di Google Maps
        
        Args:
            query: Kata kunci pencarian (contoh: "kedai kopi")
            location: Lokasi (contoh: "Jogja" atau "Yogyakarta")
            min_rating: Rating minimum (contoh: 4.0)
            max_results: Maksimal hasil yang diambil
            lat: Latitude (opsional, untuk koordinat spesifik)
            lng: Longitude (opsional, untuk koordinat spesifik)
            radius_m: Radius dalam meter (opsional, untuk area spesifik)
        
        Returns:
            List of dict dengan informasi tempat
        """
        driver = None
        try:
            print(f"[INFO] Membuat Chrome driver...")
            driver = self._get_driver()
            print(f"[INFO] Chrome driver berhasil dibuat")
            
            wait = WebDriverWait(driver, 20)
            
            # Buat URL berdasarkan koordinat atau location
            if lat and lng:
                # Gunakan format URL dengan koordinat dan radius
                if radius_m:
                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@{lat},{lng},{radius_m}m/data=!3m2!1e3!4b1?entry=ttu"
                else:
                    # Default radius 5000m jika tidak ditentukan
                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@{lat},{lng},5000m/data=!3m2!1e3!4b1?entry=ttu"
                print(f"[INFO] Menggunakan koordinat: {lat}, {lng} dengan radius: {radius_m or 5000}m")
            else:
                # Gunakan format URL biasa dengan location
                search_query = f"{query} {location}"
                url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            print(f"[INFO] Membuka URL: {url}")
            driver.get(url)
            
            # Tunggu hasil muncul
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            # Tunggu sampai hasil pencarian muncul
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']")))
                print(f"[INFO] Hasil pencarian sudah muncul")
            except:
                print(f"[INFO] Menunggu hasil pencarian...")
                time.sleep(5)
            
            # Scroll untuk memuat lebih banyak hasil
            print(f"[INFO] Scroll untuk memuat lebih banyak hasil...")
            place_elements = self._scroll_results(driver, max_results)
            
            # Tunggu sedikit lagi setelah scroll
            time.sleep(3)
            
            # Scroll ke setiap elemen secara individual untuk memastikan konten ter-load
            # Hapus batasan untuk memastikan semua elemen ter-load
            print(f"[INFO] Memastikan semua elemen ter-load dengan scroll individual...")
            print(f"[INFO] Total elemen yang akan di-scroll: {len(place_elements)}")
            
            # Scroll ke semua elemen, tidak ada batasan
            for idx, elem in enumerate(place_elements):
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", elem)
                    time.sleep(0.2)  # Sedikit lebih lama untuk memastikan loading
                    if (idx + 1) % 25 == 0:
                        print(f"[INFO] Scrolled to element {idx+1}/{len(place_elements)}")
                except:
                    pass
            
            # Tunggu lagi untuk lazy loading
            time.sleep(3)
            
            # Scroll sekali lagi ke bawah untuk memastikan semua ter-load
            try:
                sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", sidebar)
                time.sleep(2)
            except:
                pass
            
            # Ambil ulang semua elemen setelah scroll individual
            place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            print(f"[INFO] Setelah scroll individual: {len(place_elements)} elemen")
            
            # Ambil semua hasil yang sudah ter-load
            print(f"[INFO] Mengekstrak data tempat...")
            results = []
            
            # Jika tidak ada elemen dari scroll, coba ambil langsung
            if len(place_elements) == 0:
                place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                print(f"[INFO] Ditemukan {len(place_elements)} elemen tempat")
                
                # Jika masih tidak ada, coba selector alternatif
                if len(place_elements) == 0:
                    print(f"[INFO] Mencoba selector alternatif...")
                    place_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                    print(f"[INFO] Ditemukan {len(place_elements)} elemen dengan selector alternatif")
            else:
                print(f"[INFO] Total {len(place_elements)} elemen tempat ter-load")
            
            # Ekstrak data dari SEMUA elemen yang ter-load, bukan hanya max_results
            # max_results hanya digunakan untuk filtering akhir jika diperlukan
            total_to_process = len(place_elements)
            print(f"[INFO] Memproses SEMUA {total_to_process} elemen yang ter-load...")
            
            # Set untuk deduplikasi berdasarkan nama
            seen_names = set()
            
            for idx, element in enumerate(place_elements):
                try:
                    # Jika elemen adalah link, cari parent article
                    if element.tag_name == 'a':
                        try:
                            # Cari parent dengan role='article'
                            parent = element.find_element(By.XPATH, "./ancestor::div[@role='article']")
                            if parent:
                                element = parent
                        except:
                            # Jika tidak ada parent article, gunakan elemen asli
                            pass
                    
                    place_data = self._extract_place_info(element, min_rating)
                    if place_data:
                        # Deduplikasi berdasarkan nama (case-insensitive)
                        name_lower = place_data['name'].lower().strip()
                        if name_lower not in seen_names:
                            seen_names.add(name_lower)
                            results.append(place_data)
                            if (idx + 1) % 10 == 0:
                                print(f"[INFO] Berhasil mengekstrak {idx+1}/{total_to_process}: {place_data['name']} (Rating: {place_data['rating']})")
                        else:
                            if (idx + 1) % 50 == 0:
                                print(f"[INFO] Duplikat ditemukan dan diabaikan: {place_data['name']}")
                    else:
                        if (idx + 1) % 50 == 0:
                            print(f"[INFO] Elemen {idx+1} tidak memenuhi kriteria (rating < min_rating atau tidak ada nama)")
                except Exception as e:
                    if (idx + 1) % 50 == 0:
                        print(f"[GAGAL] Error extracting place info untuk elemen {idx+1}: {e}")
                    continue
            
            print(f"[INFO] Berhasil mengekstrak {len(results)} tempat (setelah deduplikasi)")
            
            # Filter berdasarkan max_results jika diperlukan (setelah ekstraksi semua)
            if max_results > 0 and len(results) > max_results:
                print(f"[INFO] Membatasi hasil dari {len(results)} menjadi {max_results} sesuai max_results")
                results = results[:max_results]
            
            # Jika hasil masih kurang dari yang diharapkan, coba teknik alternatif
            # Perbaiki kondisi: tidak perlu batasan len(results) < 20, cukup cek apakah kurang dari max_results
            if max_results > 0 and len(results) < max_results:
                print(f"[INFO] Hasil ({len(results)}) kurang dari yang diharapkan ({max_results}), mencoba teknik alternatif...")
                additional_results = self._try_alternative_scraping(driver, query, location, min_rating, seen_names)
                for res in additional_results:
                    name_lower = res['name'].lower().strip()
                    if name_lower not in seen_names:
                        seen_names.add(name_lower)
                        results.append(res)
                print(f"[INFO] Total hasil setelah teknik alternatif: {len(results)}")
                
                # Filter lagi jika melebihi max_results
                if len(results) > max_results:
                    results = results[:max_results]
            
            # Jika menggunakan koordinat dan hasil masih kurang, coba beberapa radius berbeda
            if lat and lng and max_results > 0 and len(results) < max_results:
                print(f"[INFO] Mencoba beberapa radius berbeda untuk mendapatkan lebih banyak hasil...")
                additional_results = self._try_multiple_radii(driver, query, lat, lng, min_rating, seen_names, max_results - len(results))
                results.extend(additional_results)
                print(f"[INFO] Total hasil setelah mencoba multiple radius: {len(results)}")
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            print(f"[GAGAL] Error during scraping: {error_msg}")
            # Berikan pesan error yang lebih informatif
            if "WinError 193" in error_msg or "not a valid Win32 application" in error_msg:
                raise Exception("ChromeDriver tidak kompatibel. Silakan install ulang Chrome browser atau update webdriver-manager.")
            elif "chromedriver" in error_msg.lower():
                raise Exception(f"Masalah dengan ChromeDriver: {error_msg}. Pastikan Chrome browser terinstall.")
            else:
                raise Exception(f"Error saat scraping: {error_msg}")
        finally:
            if driver:
                try:
                    driver.quit()
                    print(f"[INFO] Chrome driver ditutup")
                except:
                    pass
    
    def _scroll_results(self, driver, max_results):
        """Scroll sidebar untuk memuat lebih banyak hasil dengan teknik yang lebih efektif dan agresif"""
        place_elements = []
        try:
            # Temukan sidebar hasil
            sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            
            # Scroll lebih agresif untuk memuat lebih banyak hasil
            previous_count = 0
            scroll_attempts = 0
            no_change_count = 0
            # Tingkatkan max_scroll_attempts untuk lebih agresif
            max_scroll_attempts = max(100, max_results // 2) if max_results > 0 else 150
            
            print(f"[INFO] Mulai scroll (maksimal {max_scroll_attempts} kali)...")
            
            # Teknik khusus: scroll ke setiap elemen secara individual untuk memicu loading
            def scroll_to_each_element(elements, start_idx=0):
                """Scroll ke setiap elemen secara individual"""
                for idx, elem in enumerate(elements[start_idx:], start=start_idx):
                    try:
                        # Scroll ke elemen dengan berbagai teknik
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", elem)
                        time.sleep(0.5)  # Delay untuk lazy loading
                        
                        # Coba klik elemen untuk memicu loading lebih banyak data
                        try:
                            # Hover dulu
                            driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", elem)
                            time.sleep(0.2)
                        except:
                            pass
                        
                        # Setiap 10 elemen, cek apakah ada elemen baru
                        if (idx + 1) % 10 == 0:
                            new_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                            if len(new_elements) > len(elements):
                                print(f"[INFO] Setelah scroll ke elemen {idx+1}, ditemukan {len(new_elements)} elemen total")
                                return new_elements
                    except Exception as e:
                        print(f"[DEBUG] Error scrolling to element {idx}: {e}")
                        continue
                return elements
            
            while scroll_attempts < max_scroll_attempts:
                # Teknik 1: Scroll bertahap dengan lebih banyak step
                scroll_position = driver.execute_script("return arguments[0].scrollTop;", sidebar)
                scroll_height = driver.execute_script("return arguments[0].scrollHeight;", sidebar)
                client_height = driver.execute_script("return arguments[0].clientHeight;", sidebar)
                
                # Scroll incremental dengan lebih banyak step untuk memicu lazy loading
                steps = 10  # Tingkatkan dari 5 ke 10
                step_size = max(200, (scroll_height - scroll_position) // steps) if scroll_height > scroll_position else 400
                
                for i in range(steps):
                    new_position = scroll_position + (i + 1) * step_size
                    driver.execute_script(
                        f"arguments[0].scrollTop = {new_position};", 
                        sidebar
                    )
                    time.sleep(1.0)  # Tingkatkan delay untuk lazy loading
                
                # Teknik 2: Scroll ke bawah penuh
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;", 
                    sidebar
                )
                time.sleep(3.0)  # Tingkatkan delay
                
                # Teknik 3: Scroll naik-turun untuk memicu loading
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight - 1000;", 
                    sidebar
                )
                time.sleep(1.5)
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;", 
                    sidebar
                )
                time.sleep(2.0)
                
                # Teknik 4: Scroll ke setiap elemen yang sudah ter-load secara individual
                current_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                if len(current_elements) > previous_count:
                    print(f"[INFO] Ditemukan {len(current_elements)} elemen, scroll ke setiap elemen baru...")
                    # Scroll ke elemen baru secara individual
                    current_elements = scroll_to_each_element(current_elements, previous_count)
                
                # Teknik 5: Scroll ke semua elemen secara individual (setiap 5 scroll attempts)
                if scroll_attempts % 5 == 0 and len(current_elements) > 0:
                    print(f"[INFO] Scroll periodik ke semua elemen ({len(current_elements)} elemen)...")
                    current_elements = scroll_to_each_element(current_elements, 0)
                
                # Cek jumlah elemen yang sudah ter-load
                current_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                current_count = len(current_elements)
                
                scroll_attempts += 1
                
                # Jika tidak ada perubahan
                if current_count == previous_count:
                    no_change_count += 1
                    
                    # Coba berbagai teknik untuk memuat lebih banyak hasil
                    if no_change_count <= 3:
                        # Scroll dengan smooth scroll
                        driver.execute_script(
                            "arguments[0].scrollTo({top: arguments[0].scrollHeight, behavior: 'smooth'});", 
                            sidebar
                        )
                        time.sleep(3.0)
                    elif no_change_count <= 6:
                        # Scroll lebih jauh
                        driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight + 3000;", 
                            sidebar
                        )
                        time.sleep(3.0)
                    elif no_change_count <= 9:
                        # Coba klik beberapa elemen terakhir untuk memicu loading
                        try:
                            if current_elements:
                                # Klik 3 elemen terakhir
                                for i in range(min(3, len(current_elements))):
                                    try:
                                        last_elem = current_elements[-(i+1)]
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", last_elem)
                                        time.sleep(0.5)
                                        try:
                                            last_elem.click()
                                            time.sleep(1.5)
                                        except:
                                            pass
                                    except:
                                        continue
                        except:
                            pass
                    elif no_change_count <= 12:
                        # Coba klik tombol "Show more" atau "Load more" dengan berbagai selector
                        try:
                            before_count = len(driver.find_elements(By.CSS_SELECTOR, "div[role='article']"))
                            
                            show_more_selectors = [
                                "button[aria-label*='more']",
                                "button[aria-label*='More']",
                                "button[aria-label*='Tampilkan']",
                                "button[aria-label*='tampilkan']",
                                "div[role='button'][aria-label*='more']",
                                "div[role='button'][aria-label*='More']",
                                "a[aria-label*='more']",
                                "a[aria-label*='More']",
                                "button[jsaction*='pane.pagination.next']"
                            ]
                            
                            for selector in show_more_selectors:
                                try:
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for btn in buttons:
                                        try:
                                            if btn.is_displayed() and btn.is_enabled():
                                                print(f"[INFO] Menemukan tombol 'Show more' dengan selector: {selector}")
                                                btn.click()
                                                time.sleep(4)
                                                
                                                after_count = len(driver.find_elements(By.CSS_SELECTOR, "div[role='article']"))
                                                if after_count > before_count:
                                                    print(f"[INFO] Tombol berhasil memuat {after_count - before_count} elemen baru")
                                                    no_change_count = 0
                                                    break
                                        except:
                                            continue
                                    if no_change_count == 0:
                                        break
                                except:
                                    continue
                        except Exception as e:
                            print(f"[DEBUG] Error mencari tombol show more: {e}")
                    elif no_change_count <= 15:
                        # Coba scroll dengan keyboard (Page Down, END)
                        try:
                            sidebar.send_keys(Keys.PAGE_DOWN)
                            time.sleep(2)
                            sidebar.send_keys(Keys.PAGE_DOWN)
                            time.sleep(2)
                            sidebar.send_keys(Keys.END)
                            time.sleep(3)
                        except:
                            pass
                    else:
                        # Coba cari dan klik elemen dengan text "Show more" menggunakan XPath
                        try:
                            xpath_selectors = [
                                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]",
                                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'tampilkan')]",
                                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load')]",
                                "//div[@role='button'][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]",
                                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]"
                            ]
                            
                            for xpath in xpath_selectors:
                                try:
                                    buttons = driver.find_elements(By.XPATH, xpath)
                                    for btn in buttons:
                                        try:
                                            if btn.is_displayed() and btn.is_enabled():
                                                print(f"[INFO] Menemukan tombol 'Show more' dengan XPath")
                                                btn.click()
                                                time.sleep(4)
                                                no_change_count = 0
                                                break
                                        except:
                                            continue
                                    if no_change_count == 0:
                                        break
                                except:
                                    continue
                            
                            # Jika XPath tidak berhasil, coba dengan text biasa
                            if no_change_count > 0:
                                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                                for btn in all_buttons:
                                    try:
                                        if not btn.is_displayed():
                                            continue
                                        btn_text = btn.text.lower()
                                        if 'more' in btn_text or 'tampilkan' in btn_text or 'load' in btn_text:
                                            print(f"[INFO] Menemukan tombol dengan text: {btn.text}")
                                            btn.click()
                                            time.sleep(4)
                                            no_change_count = 0
                                            break
                                    except:
                                        continue
                        except Exception as e:
                            print(f"[DEBUG] Error mencari tombol: {e}")
                            pass
                    
                    # Jika tidak ada perubahan setelah banyak percobaan, coba teknik terakhir
                    if no_change_count > 20:
                        print(f"[INFO] Tidak ada hasil baru setelah {scroll_attempts} scroll (no change: {no_change_count})")
                        # Coba scroll ke setiap elemen sekali lagi
                        try:
                            all_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                            print(f"[INFO] Mencoba scroll ke semua {len(all_elements)} elemen sekali lagi...")
                            for elem in all_elements:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.3)
                                except:
                                    pass
                            time.sleep(3)
                            final_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                            if len(final_elements) > current_count:
                                current_count = len(final_elements)
                                no_change_count = 0
                                print(f"[INFO] Setelah scroll ulang, ditemukan {current_count} elemen")
                            else:
                                print(f"[INFO] Tidak ada elemen baru setelah scroll ulang. Total: {current_count}")
                                break
                        except:
                            break
                else:
                    no_change_count = 0  # Reset counter jika ada perubahan
                    print(f"[INFO] Scroll {scroll_attempts}: Ditemukan {current_count} elemen (bertambah {current_count - previous_count})")
                
                previous_count = current_count
                
                # Jika sudah mencapai max_results dan max_results > 0, stop
                if max_results > 0 and current_count >= max_results:
                    print(f"[INFO] Sudah mencapai target {max_results} hasil")
                    break
            
            # Tunggu lebih lama untuk memastikan semua konten ter-load
            time.sleep(3)
            
            # Scroll sekali lagi ke semua elemen untuk memastikan semua ter-load
            try:
                all_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                print(f"[INFO] Final scroll ke semua {len(all_elements)} elemen...")
                for elem in all_elements:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(0.2)
                    except:
                        pass
                time.sleep(2)
                
                # Scroll ke bawah sekali lagi
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", sidebar)
                time.sleep(2)
            except:
                pass
            
            # Ambil semua elemen yang ter-load
            place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            print(f"[INFO] Total {len(place_elements)} elemen setelah scroll")
            
            return place_elements
            
        except Exception as e:
            print(f"[GAGAL] Error scrolling: {e}")
            # Coba ambil elemen yang sudah ter-load
            try:
                place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                return place_elements
            except:
                return []
    
    def _try_multiple_radii(self, driver, query, lat, lng, min_rating, seen_names, target_count):
        """Mencoba beberapa radius berbeda untuk mendapatkan lebih banyak hasil"""
        additional_results = []
        try:
            # Daftar radius yang akan dicoba (dalam meter)
            radii = [1000, 2000, 3000, 5000, 10000, 15000, 20000]
            
            print(f"[INFO] Mencoba {len(radii)} radius berbeda...")
            
            for radius in radii:
                if len(additional_results) >= target_count:
                    break
                    
                try:
                    print(f"[INFO] Mencoba radius {radius}m...")
                    
                    # Buat URL dengan radius baru
                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@{lat},{lng},{radius}m/data=!3m2!1e3!4b1?entry=ttu"
                    driver.get(url)
                    
                    # Tunggu hasil muncul
                    time.sleep(3)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
                        )
                    except:
                        pass
                    
                    # Scroll untuk memuat hasil
                    try:
                        sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
                        for _ in range(3):
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", sidebar)
                            time.sleep(1.5)
                    except:
                        pass
                    
                    # Ambil elemen
                    place_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    print(f"[INFO] Radius {radius}m: Ditemukan {len(place_elements)} elemen")
                    
                    # Ekstrak data
                    for elem in place_elements:
                        try:
                            place_data = self._extract_place_info(elem, min_rating)
                            if place_data:
                                name_lower = place_data['name'].lower().strip()
                                if name_lower not in seen_names:
                                    seen_names.add(name_lower)
                                    additional_results.append(place_data)
                                    print(f"[INFO] Berhasil mengekstrak dari radius {radius}m: {place_data['name']}")
                                    if len(additional_results) >= target_count:
                                        break
                        except:
                            continue
                    
                except Exception as e:
                    print(f"[DEBUG] Error dengan radius {radius}m: {e}")
                    continue
            
            print(f"[INFO] Multiple radius menghasilkan {len(additional_results)} hasil tambahan")
            return additional_results
            
        except Exception as e:
            print(f"[GAGAL] Error dalam multiple radius: {e}")
            return []
    
    def _try_alternative_scraping(self, driver, query, location, min_rating, seen_names):
        """Mencoba teknik alternatif untuk mendapatkan lebih banyak hasil"""
        additional_results = []
        try:
            print(f"[INFO] Mencoba teknik alternatif: mengklik marker di peta...")
            
            # Coba klik beberapa marker di peta untuk memuat lebih banyak hasil
            try:
                # Cari marker di peta
                markers = driver.find_elements(By.CSS_SELECTOR, 
                    "div[role='button'][aria-label*='hotel'], "
                    "div[role='button'][aria-label*='Hotel'], "
                    "[data-value='Name']")
                
                print(f"[INFO] Ditemukan {len(markers)} marker di peta")
                
                # Klik beberapa marker untuk memuat lebih banyak hasil di sidebar
                for i, marker in enumerate(markers[:10]):  # Batasi 10 marker
                    try:
                        marker.click()
                        time.sleep(1.5)
                        
                        # Cek apakah ada elemen baru di sidebar
                        new_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                        if len(new_elements) > 0:
                            # Coba ekstrak dari elemen terakhir (yang baru diklik)
                            if len(new_elements) > i:
                                try:
                                    place_data = self._extract_place_info(new_elements[-1], min_rating)
                                    if place_data:
                                        name_lower = place_data['name'].lower().strip()
                                        if name_lower not in seen_names:
                                            seen_names.add(name_lower)
                                            additional_results.append(place_data)
                                            print(f"[INFO] Berhasil mengekstrak dari marker: {place_data['name']}")
                                except:
                                    pass
                    except:
                        continue
                
                # Setelah klik marker, coba scroll lagi
                try:
                    sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", sidebar)
                    time.sleep(2)
                    
                    # Ambil elemen baru
                    all_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    for elem in all_elements:
                        try:
                            place_data = self._extract_place_info(elem, min_rating)
                            if place_data:
                                name_lower = place_data['name'].lower().strip()
                                if name_lower not in seen_names:
                                    seen_names.add(name_lower)
                                    additional_results.append(place_data)
                        except:
                            continue
                except:
                    pass
                    
            except Exception as e:
                print(f"[DEBUG] Error dalam teknik alternatif: {e}")
            
            print(f"[INFO] Teknik alternatif menghasilkan {len(additional_results)} hasil tambahan")
            return additional_results
            
        except Exception as e:
            print(f"[GAGAL] Error dalam teknik alternatif: {e}")
            return []
    
    def _extract_place_info(self, element, min_rating):
        """Ekstrak informasi dari elemen tempat dengan teknik yang lebih robust"""
        try:
            # Ambil semua text dari element untuk parsing manual jika selector gagal
            element_text = ""
            try:
                element_text = element.text
            except:
                pass
            
            # Nama tempat - coba beberapa selector dengan lebih banyak opsi
            name = "N/A"
            name_selectors = [
                "div[data-value='Name']",
                "a[data-value='Name']",
                "div.fontHeadlineSmall",
                "div[jslog*='name']",
                "h3",
                "h2",
                "h1",
                "div[role='button'] span",
                "a[href*='/maps/place/']",
                "div[role='heading']",
                "span.fontHeadlineSmall",
                "div.fontHeadlineMedium"
            ]
            for selector in name_selectors:
                try:
                    name_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if name_elem:
                        for elem in name_elem:
                            text = elem.text.strip()
                            if text and len(text) > 0 and len(text) < 200:  # Validasi panjang nama
                                # Skip jika text mengandung pattern rating atau review
                                if not re.search(r'^\d+[.,]\d+\s*(?:star|bintang)', text, re.IGNORECASE):
                                    name = text
                                    break
                        if name != "N/A":
                            break
                except:
                    continue
            
            # Jika masih tidak ada nama dari selector, coba parse dari text element
            if name == "N/A" and element_text:
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                # Nama biasanya di baris pertama yang tidak mengandung rating/review
                for line in lines[:5]:  # Cek 5 baris pertama
                    if line and len(line) > 0 and len(line) < 200:
                        # Skip jika mengandung pattern rating/review/alamat
                        if not re.search(r'^\d+[.,]\d+\s*(?:star|bintang)', line, re.IGNORECASE) and \
                           not re.search(r'\d+\s*(?:review|ulasan)', line, re.IGNORECASE) and \
                           not re.search(r'^[A-Za-z\s]+,\s*[A-Za-z\s]+$', line):  # Pattern alamat
                            name = line
                            break
            
            # Rating - coba beberapa selector dengan lebih banyak opsi
            rating = 0.0
            rating_selectors = [
                "span[aria-label*='Bintang']",
                "span[aria-label*='bintang']",
                "span[aria-label*='star']",
                "span[aria-label*='Star']",
                "span[aria-label*='rating']",
                "span[aria-label*='Rating']",
                "div.fontBodyMedium span[aria-label]",
                "span[aria-label*='⭐']",
                "div[aria-label*='star']",
                "div[aria-label*='Star']"
            ]
            for selector in rating_selectors:
                try:
                    rating_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if rating_elem:
                        for elem in rating_elem:
                            rating_text = elem.get_attribute("aria-label") or elem.text
                            if rating_text:
                                # Cari pattern rating: "4.5" atau "4,5" atau "4"
                                rating_match = re.search(r'(\d+[.,]\d+|\d+)', rating_text)
                                if rating_match:
                                    rating_val = float(rating_match.group(1).replace(',', '.'))
                                    if 0 <= rating_val <= 5:  # Validasi range rating
                                        rating = rating_val
                                        break
                        if rating > 0:
                            break
                except:
                    continue
            
            # Jika tidak ada rating dari aria-label, cari di text dengan berbagai pattern
            if rating == 0.0 and element_text:
                # Pattern: "4.5 star", "4,5 bintang", "4.5⭐", dll
                rating_patterns = [
                    r'(\d+[.,]\d+)\s*(?:star|bintang|⭐)',
                    r'(\d+[.,]\d+)\s*/\s*5',
                    r'Rating[:\s]*(\d+[.,]\d+|\d+)',
                    r'(\d+[.,]\d+|\d+)\s*(?:out of|dari)\s*5'
                ]
                for pattern in rating_patterns:
                    rating_match = re.search(pattern, element_text, re.IGNORECASE)
                    if rating_match:
                        rating_val = float(rating_match.group(1).replace(',', '.'))
                        if 0 <= rating_val <= 5:
                            rating = rating_val
                            break
            
            # Filter berdasarkan rating minimum
            if rating < min_rating:
                return None
            
            # Jumlah review - coba beberapa selector dengan lebih banyak opsi
            review_count = 0
            review_selectors = [
                "span[aria-label*='review']",
                "span[aria-label*='Review']",
                "span[aria-label*='ulasan']",
                "span[aria-label*='Ulasan']",
                "span.fontBodyMedium",
                "div.fontBodyMedium"
            ]
            for selector in review_selectors:
                try:
                    review_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if review_elem:
                        for elem in review_elem:
                            review_text = elem.get_attribute("aria-label") or elem.text
                            if review_text and ('review' in review_text.lower() or 'ulasan' in review_text.lower()):
                                # Cari angka dalam text review
                                review_match = re.search(r'(\d+)', review_text.replace(',', '').replace('.', ''))
                                if review_match:
                                    review_count = int(review_match.group(1))
                                    break
                        if review_count > 0:
                            break
                except:
                    continue
            
            # Jika tidak ada dari selector, cari di text dengan berbagai pattern
            if review_count == 0 and element_text:
                review_patterns = [
                    r'(\d+)\s*(?:review|ulasan)',
                    r'(\d+)\s*(?:reviews|reviews)',
                    r'(\d+)\s*(?:rating|ratings)'
                ]
                for pattern in review_patterns:
                    review_match = re.search(pattern, element_text, re.IGNORECASE)
                    if review_match:
                        review_count = int(review_match.group(1))
                        break
            
            # Kategori/Tipe - parsing yang lebih baik
            category = "N/A"
            category_selectors = [
                "div[data-value='Category']",
                "div.fontBodyMedium",
                "span.fontBodyMedium",
                "div[jslog*='category']",
                "span[jslog*='category']"
            ]
            
            # Coba dari selector
            for selector in category_selectors:
                try:
                    category_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if category_elem:
                        for elem in category_elem:
                            cat_text = elem.text.strip()
                            # Validasi: panjang wajar, tidak mengandung rating, tidak seperti alamat
                            if cat_text and len(cat_text) < 100 and \
                               not re.search(r'\d+[.,]\d+', cat_text) and \
                               not re.search(r'^\d+', cat_text) and \
                               not re.search(r',\s*[A-Z]{2}\s*\d', cat_text):  # Pattern alamat US
                                category = cat_text
                                break
                        if category != "N/A":
                            break
                except:
                    continue
            
            # Jika tidak ada dari selector, coba parse dari text
            if category == "N/A" and element_text:
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                # Kategori biasanya setelah nama, sebelum rating/alamat
                for i, line in enumerate(lines[1:4]):  # Cek baris 2-4
                    if line and len(line) < 100 and \
                       not re.search(r'\d+[.,]\d+', line) and \
                       not re.search(r'^\d+', line) and \
                       not re.search(r'(?:review|ulasan|star|bintang)', line, re.IGNORECASE) and \
                       not re.search(r'^[A-Za-z\s]+,\s*[A-Za-z\s]+', line):  # Pattern alamat
                        category = line
                        break
            
            # Alamat - parsing yang lebih baik
            address = "N/A"
            address_selectors = [
                "div[data-value='Address']",
                "div.fontBodyMedium",
                "span.fontBodyMedium",
                "div[jslog*='address']",
                "span[jslog*='address']"
            ]
            
            # Coba dari selector
            for selector in address_selectors:
                try:
                    address_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if address_elem:
                        for elem in address_elem:
                            addr_text = elem.text.strip()
                            # Validasi: panjang wajar, mengandung pattern alamat
                            if addr_text and len(addr_text) > 10 and \
                               (',' in addr_text or re.search(r'\d+', addr_text)):  # Alamat biasanya ada koma atau angka
                                address = addr_text
                                break
                        if address != "N/A":
                            break
                except:
                    continue
            
            # Jika tidak ada dari selector, cari di text dengan pattern alamat
            if address == "N/A" and element_text:
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                # Alamat biasanya di baris setelah kategori, mengandung koma atau angka
                for i, line in enumerate(lines):
                    if i > 0 and len(line) > 10 and \
                       (',' in line or re.search(r'\d+', line)) and \
                       not re.search(r'^\d+[.,]\d+', line) and \
                       not re.search(r'(?:review|ulasan|star|bintang)', line, re.IGNORECASE):
                        address = line
                        break
            
            # Link
            link = ""
            link_selectors = [
                "a[href*='/maps/place/']",
                "a[data-value='Directions']",
                "a[href*='google.com/maps']"
            ]
            for selector in link_selectors:
                try:
                    link_elem = element.find_elements(By.CSS_SELECTOR, selector)
                    if link_elem:
                        link = link_elem[0].get_attribute("href")
                        if link:
                            break
                except:
                    continue
            
            # Validasi: minimal harus ada nama
            if name == "N/A" or not name or len(name.strip()) == 0:
                return None
            
            return {
                'name': name.strip(),
                'rating': rating,
                'review_count': review_count,
                'category': category.strip() if category != "N/A" else "N/A",
                'address': address.strip() if address != "N/A" else "N/A",
                'link': link
            }
            
        except Exception as e:
            print(f"[GAGAL] Error extracting place info: {e}")
            # Debug: print element text untuk troubleshooting
            try:
                print(f"[DEBUG] Element text: {element.text[:300]}")
            except:
                pass
            return None
