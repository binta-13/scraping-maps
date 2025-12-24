#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd

import logging
import logging.config
import yaml
import mysql.connector
from dotenv import load_dotenv

from utils.transform_data import transform_data
from utils.load_to_mysql import load_to_mysql
from utils.extract_csv import extract_xlsx  # kita asumsikan ini bisa dipakai untuk read_excel

# Memuat file .env
load_dotenv()

def setup_logging(logging_config_file):
    """
    Mengatur logging berdasarkan konfigurasi YAML.
    """
    if not os.path.exists(logging_config_file):
        raise FileNotFoundError(f"Konfigurasi logging file '{logging_config_file}' tidak ditemukan.")
    with open(logging_config_file, 'r') as file:
        config = yaml.safe_load(file)
    logging.config.dictConfig(config['logging'])

def list_apps(data_root):
    """
    Mengambil daftar folder di dalam data_root sebagai daftar aplikasi.
    """
    apps = []
    for item in os.listdir(data_root):
        path_item = os.path.join(data_root, item)
        if os.path.isdir(path_item):
            apps.append(item)
    return apps

def select_app(apps):
    """
    Menampilkan daftar aplikasi dan meminta user memilih salah satunya.
    """
    print("Pilih aplikasi yang akan dimigrasi:")
    for idx, app_name in enumerate(apps, start=1):
        print(f"{idx}. {app_name}")
    choice = input("Masukkan nomor pilihan: ").strip()
    try:
        choice_int = int(choice)
        if 1 <= choice_int <= len(apps):
            return apps[choice_int - 1]
        else:
            print("Pilihan tidak valid.")
            sys.exit(1)
    except ValueError:
        print("Input harus berupa angka.")
        sys.exit(1)

def select_environment():
    """
    Meminta user memilih environment (local/dev/production).
    """
    env = input("Pilih environment (local/dev/production): ").strip().lower()
    if env not in ['local','dev','production']:
        print("Environment tidak valid.")
        sys.exit(1)
    return env

def get_db_connection(env):
    """
    Membuat koneksi database berdasarkan environment (local/dev/production).
    Mengambil informasi koneksi dari file .env.
    """
    # Menentukan prefix untuk variabel lingkungan sesuai dengan environment
    db_service_key = f"DB_{env.upper()}"

    # Ambil konfigurasi dari file .env
    db_host = os.getenv(f"{db_service_key}_HOST")
    db_port = os.getenv(f"{db_service_key}_PORT")
    db_user = os.getenv(f"{db_service_key}_USER")
    db_password = os.getenv(f"{db_service_key}_PASSWORD")
    db_name = os.getenv(f"{db_service_key}_NAME")
    db_charset = os.getenv(f"{db_service_key}_CHARSET")
    db_collation = os.getenv(f"{db_service_key}_COLLATION")

    # Cek apakah semua variabel lingkungan ada
    if not all([db_host, db_port, db_user, db_password, db_name]):
        logger.critical(f"Konfigurasi database untuk environment '{env}' tidak lengkap di file .env.")
        sys.exit(1)

    # Siapkan parameter koneksi
    conn_params = {
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "password": db_password,
        "database": db_name,
        "charset": db_charset,
        "collation": db_collation
    }

    # Membuat koneksi ke database
    try:
        conn = mysql.connector.connect(**conn_params)
        print('conn: ', conn)
        logger.info("Koneksi database berhasil dibuat.")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Gagal membuat koneksi database: {err}")
        sys.exit(1)

def migrasi_app(app_folder, env, base_path, dry_run=False):
    """
    Proses migrasi data untuk satu aplikasi.
    Mencari file Excel di data_import_to_db, lalu memproses setiap sheet.
    """
    logger.info(f"Memulai migrasi untuk aplikasi: {app_folder} pada environment: {env}")
    data_import_dir = os.path.join(base_path, "data", app_folder, "data_import_to_db")

    # Cari file excel di folder data_import_to_db
    # Asumsi kita hanya memproses file <nama_app>.xlsx. 
    # Atau jika mau lebih fleksibel, cari file .xlsx apapun.
    excel_files = [f for f in os.listdir(data_import_dir) if f.endswith(".xlsx")]
    if not excel_files:
        logger.error(f"Tidak ditemukan file .xlsx di {data_import_dir}")
        return

    excel_path = os.path.join(data_import_dir, excel_files[0])  # ambil file pertama
    logger.info(f"Menggunakan file Excel: {excel_files[0]}")

    # Baca semua sheet
    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    except Exception as e:
        logger.error(f"Gagal membaca file Excel: {e}")
        sys.exit(1)

    # Buat koneksi database
    db_conn = get_db_connection(env)

    # Iterasi setiap sheet -> table_name = nama sheet
    for sheet_name, df_sheet in all_sheets.items():
        if df_sheet.empty:
            logger.info(f"Sheet '{sheet_name}' kosong, dilewati.")
            continue

        table_name = sheet_name.lower()  # Asumsi nama tabel = nama sheet
        logger.info(f"Memproses sheet '{sheet_name}' -> tabel '{table_name}'")

        # Dry run: cek apakah df_sheet valid (transform_data)
        if dry_run:
            try:
                _df_tmp, valid_cols = transform_data(df_sheet, table_name, db_conn)
                logger.info(f"Dry-run OK untuk sheet '{sheet_name}' (tabel '{table_name}').")
            except Exception as e:
                logger.error(f"Dry-run gagal untuk sheet '{sheet_name}': {e}")
                logger.error("Menghentikan proses migrasi.")
                db_conn.close()
                sys.exit(1)
        else:
            # Jalankan ETL nyata
            # Extract (sudah di all_sheets -> df_sheet)
            # Transform
            try:
                df_transformed, valid_cols = transform_data(df_sheet, table_name, db_conn)
                
                # Handle datetime columns
                cursor = db_conn.cursor()
                cursor.execute(f"DESCRIBE {table_name}")
                columns_info = cursor.fetchall()
                
                for col in valid_cols:
                    # Check if column is datetime type in MySQL
                    col_type = next((info[1] for info in columns_info if info[0].lower() == col.lower()), None)
                    if col_type and ('datetime' in col_type.lower() or 'timestamp' in col_type.lower()):
                        # First try standard conversion
                        df_transformed[col] = pd.to_datetime(df_transformed[col], errors='coerce')
                        
                        # For any values that might be in date-only format (e.g. '2019-09-13')
                        # Try to convert them as date-only and then add time component
                        date_only_mask = df_transformed[col].isna()
                        if date_only_mask.any():
                            # Try to parse date-only strings for the NULL values
                            date_values = df_sheet[col].loc[date_only_mask.values]
                            if not date_values.empty:
                                try:
                                    # Convert dates to datetime with time component
                                    temp_dates = pd.to_datetime(date_values, errors='coerce')
                                    # Update the original dataframe with these values
                                    df_transformed.loc[date_only_mask, col] = temp_dates
                                    logger.info(f"Recovered {temp_dates.count()} date-only values for column {col}")
                                except Exception as e:
                                    logger.warning(f"Error converting date-only values for {col}: {e}")
                        
                        # Convert NaT to None/NULL for database insertion
                        df_transformed[col] = df_transformed[col].astype(object).where(df_transformed[col].notnull(), None)
                        logger.info(f"Converting datetime column {col}, date-only values will be stored as 00:00:00")

                cursor.close()
            except Exception as e:
                logger.error(f"Transform gagal untuk sheet '{sheet_name}': {e}")
                logger.error("Menghentikan proses migrasi.")
                db_conn.close()
                sys.exit(1)

            # Load
            try:
                load_to_mysql(df_transformed, table_name, valid_cols, db_conn, env, app_folder)
            except Exception as e:
                logger.error(f"Load gagal untuk sheet '{sheet_name}': {e}")
                logger.error("Menghentikan proses migrasi.")
                db_conn.close()
                sys.exit(1)

    db_conn.close()
    logger.info("Koneksi database ditutup.")
    logger.info(f"Proses migrasi untuk aplikasi '{app_folder}' selesai.")

def main():
    # Setup logging
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(base_dir)
    logging_config_file = os.path.join(base_dir, 'config', 'config_logging.yaml')
    if not os.path.exists(logging_config_file):
        raise FileNotFoundError(f"File konfigurasi logging '{logging_config_file}' tidak ditemukan.")
    
    try:
        setup_logging(logging_config_file)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    global logger
    logger = logging.getLogger(__name__)

    # Parse argumen (opsional)
    parser = argparse.ArgumentParser(description="Migrasi data multi-sheet Excel.")
    parser.add_argument("--dry-run", action="store_true", help="Hanya cek data tanpa insert ke database.")
    args = parser.parse_args()
    dry_run = args.dry_run

    # Hitung base_path
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # List aplikasi di /data
    data_root = os.path.join(base_path, "data")
    apps = list_apps(data_root)
    if not apps:
        logger.error("Tidak ada aplikasi yang ditemukan di folder data.")
        sys.exit(1)

    selected_app = select_app(apps)
    selected_env = select_environment()

    migrasi_app(selected_app, selected_env, base_path, dry_run=dry_run)

    if dry_run:
        logger.info("Dry-run migrasi selesai, tidak ada data yang dimasukkan ke DB.")
    else:
        logger.info("Migrasi selesai.")

if __name__ == "__main__":
    main()
