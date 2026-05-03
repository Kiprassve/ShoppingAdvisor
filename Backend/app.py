import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from Crawler.Crawler.Crawler import Rimi_crawler
import psycopg2
import os

app = Flask(__name__, static_folder='static')
CORS(app)

DB_URL = os.environ.get("DATABASE_URL","postgresql://postgres:password123@db:5432/map_demo")

@app.route('/api/scrape', methods=['GET'])
def get_data():
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Gauname reikšmes iš main.js GetStores funkcijos ar parduotuvė egzistuoja duotam spinduliui
    exist_maxima = request.args.get('maxima', 'false').lower() == 'true'
    exist_rimi = request.args.get('rimi', 'false').lower() == 'true'
    exist_iki = request.args.get('iki', 'false').lower() == 'true'
    # Nustatome kelius iki tavo JSON failų
    # Jei app.py yra "Backend" aplanke, o failai "Backend/Crawler/...", kelias bus toks:
    rimi_path = os.path.join(base_path, "Crawler", "Crawler", "products.json")
    iki_path = os.path.join(base_path, "Crawler", "Crawler", "IKI_products.json")

    print(f"\nDEBUG: Ieškau failo čia -> {rimi_path}")
    print(f"DEBUG: Ar failas egzistuoja? -> {os.path.exists(rimi_path)}")
    data = []

    # --- 1. RIMI DUOMENŲ APDOROJIMAS ---
    if os.path.exists(rimi_path) and exist_rimi:
        try:
            with open(rimi_path, "r", encoding="utf-8") as f:
                rimi_products = json.load(f)
                for p in rimi_products:
                    try:
                        # Naudojame .get(), kad programa nenulūžtų, jei trūksta lauko
                        p_discount = str(p.get('price_discount', '0')).replace(',', '.').strip()
                        p_price = str(p.get('price', '0')).replace(',', '.').strip()
                        
                        if p_discount != "0" and p_discount != "":
                            final_price = float(p_discount)
                        else:
                            final_price = float(p_price)

                        data.append({
                            "name": p.get('name'),
                            "price": final_price,
                            "image": p.get('image_url'),
                            "baltymai": float(str(p.get('protein', '0')).replace(',', '.')),
                            "angliavandeniai": float(str(p.get('carbohydrates', '0')).replace(',', '.')),
                            "riebalai": float(str(p.get('fat', '0')).replace(',', '.')),
                            "calories": float(p.get('calories_kcal', 0)),
                            "store": "Rimi",
                            "storeLogo": "http://127.0.0.1:5000/static/Icons/rimi_logo.png"
                        })
                    except Exception:
                        continue
        except Exception as e:
            print(f"Klaida skaitant Rimi failą: {e}")

    # --- 2. IKI DUOMENŲ APDOROJIMAS ---
    if os.path.exists(iki_path):
        try:
            with open(iki_path, "r", encoding="utf-8") as f:
                iki_products = json.load(f)
                for p in iki_products:
                    try:
                        p_discount = str(p.get('price_discount', '0')).replace(',', '.').strip()
                        p_price = str(p.get('price', '0')).replace(',', '.').strip()
                        
                        if p_discount != "0" and p_discount != "":
                            final_price = float(p_discount)
                        else:
                            final_price = float(p_price)

                        data.append({
                            "name": p.get('name'),
                            "price": final_price,
                            "image": p.get('image_url'),
                            "baltymai": float(str(p.get('protein', '0')).replace(',', '.')),
                            "angliavandeniai": float(str(p.get('carbohydrates', '0')).replace(',', '.')),
                            "riebalai": float(str(p.get('fat', '0')).replace(',', '.')),
                            "calories": float(p.get('calories_kcal', 0)),
                            "store": "Iki",
                            "storeLogo": "http://127.0.0.1:5000/static/Icons/iki_logo.png"
                        })
                    except Exception:
                        continue
        except Exception as e:
            print(f"Klaida skaitant Iki failą: {e}")

    # Grąžiname visus surinktus duomenis (apribojame nuo 800 iki 830)
    return jsonify(data[800:830])

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