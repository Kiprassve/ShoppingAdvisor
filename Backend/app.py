import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from Crawler.Crawler.Crawler import Rimi_crawler
import psycopg2
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "map_demo")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password123")
DB_PORT = os.environ.get("DB_PORT", "5432")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logo_mapping = {
    "maxima": "http://127.0.0.1:5000/static/Icons/maxima_logo.png",
    "rimi": "http://127.0.0.1:5000/static/Icons/rimi_logo.png",
    "iki": "http://127.0.0.1:5000/static/Icons/iki_logo.png"
}

@app.route('/api/scrape', methods=['GET'])
def get_data():
    # 1. Gauname filtrus iš užklausos
    exist_rimi = request.args.get('rimi', 'false').lower()
    exist_iki = request.args.get('iki', 'false').lower()
    
    # 2. Profesionalus puslapiavimas: gauname page ir per_page parametrus
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)  # Nutylėjimas – 5 prekės puslapyje
    
    # Apsauga nuo neigiamų skaičių
    if page < 1: page = 1
    if per_page < 1: per_page = 5
    
    # SQL poslinkio (OFFSET) skaičiavimas
    offset = (page - 1) * per_page

    stores_to_fetch = []
    if exist_rimi == 'true': stores_to_fetch.append('Rimi')
    if exist_iki == 'true': stores_to_fetch.append('Iki')

    if not stores_to_fetch:
        return jsonify({
            "products": [],
            "total_items": 0,
            "total_pages": 0,
            "current_page": page
        })

    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # 3. Pirmiausia sužinome, KIEK IŠ VISO prekių atitinka filtrą duomenų bazėje
        count_query = """
            SELECT COUNT(*) FROM products WHERE store_name = ANY(%s);
        """
        cursor.execute(count_query, (stores_to_fetch,))
        total_items = cursor.fetchone()[0]
        
        # Apskaičiuojame bendrą puslapių skaičių
        import math
        total_pages = math.ceil(total_items / per_page)
        
        # 4. Paimame TIK to puslapio duomenis naudodami LIMIT ir OFFSET
        query = """
            SELECT name, price, image_url, protein, carbohydrates, fat, calories, store_name, weight 
            FROM products 
            WHERE store_name = ANY(%s)
            ORDER BY id DESC
            LIMIT %s OFFSET %s;
        """
        cursor.execute(query, (stores_to_fetch, per_page, offset))
        rows = cursor.fetchall()
        
        products_list = []
        for row in rows:
            store_name_raw = row[7] or ""
            store_name_lower = store_name_raw.lower().strip()
            
            matched_logo = "/static/Icons/default_logo.png"
            for brand in logo_mapping:
                if brand in store_name_lower:
                    matched_logo = logo_mapping[brand]
                    break

            products_list.append({
                "name": row[0],
                "price": float(row[1]),
                "image": row[2],
                "baltymai": float(row[3] or 0),
                "angliavandeniai": float(row[4] or 0),
                "riebalai": float(row[5] or 0),
                "calories": float(row[6] or 0),
                "store": row[7],
                "storeLogo": matched_logo,
                "weight": row[8]
            })
            
        # 5. Grąžiname struktūrizuotą atsakią su puslapiavimo meta-duomenimis
        return jsonify({
            "products": products_list,
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page
        })
    
    except Exception as e:
        print(f"Klaida imant duomenis iš DB: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/stores', methods=['GET'])
def get_stores():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', type=float)

    if not all([lat, lon, radius]):
        return jsonify({"error": "Missing lat, lon, or radius"}), 400

    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Kadangi stulpelių su dvitaškiais nėra, o 'tags' neegzistuoja, 
        # naudojame tik saugius, standartinius OSM stulpelius.
        # COALESCE padeda išvengti NULL reikšmių.
        sql = """
            SELECT 
                name, 
                ST_Y(ST_Transform(way, 4326)) as lat, 
                ST_X(ST_Transform(way, 4326)) as lon,
                'Informacija neprieinama' as opening_hours,
                'Nėra svetainės' as website,
                COALESCE(name, 'Parduotuvė') as address
            FROM planet_osm_point 
            WHERE shop IS NOT NULL 
            AND ST_DWithin(
                ST_Transform(way, 4326)::geography, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                %s
            )
            UNION ALL
            SELECT 
                name, 
                ST_Y(ST_Transform(ST_Centroid(way), 4326)) as lat, 
                ST_X(ST_Transform(ST_Centroid(way), 4326)) as lon,
                'Informacija neprieinama' as opening_hours,
                'Nėra svetainės' as website,
                COALESCE(name, 'Parduotuvė') as address
            FROM planet_osm_polygon 
            WHERE shop IS NOT NULL 
            AND ST_DWithin(
                ST_Transform(way, 4326)::geography, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                %s
            );
        """
        
        cursor.execute(sql, (lon, lat, radius, lon, lat, radius))
        rows = cursor.fetchall()
        
        stores = []
        for row in rows:
            stores.append({
                "name": row[0] if row[0] else "Parduotuvė",
                "lat": row[1],
                "lon": row[2],
                "opening_hours": row[3],
                "website": row[4],
                "address": row[5] # Naudojame pavadinimą kaip adresą, nes kiti laukai DB neegzistuoja
            })
            
        return jsonify(stores)
    
    except Exception as e:
        print("Database error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# SVARBU: Įsitikink, kad virš šios eilutės NĖRA jokio kito Rimi_crawler(url) kvietimo!
if __name__ == '__main__':
    print("Flask serveris startuoja ant porto 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)