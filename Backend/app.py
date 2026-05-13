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
    # Gauname filtrus iš užklausos (pvz., ?rimi=true&iki=true)
    exist_rimi = request.args.get('rimi', 'false').lower()
    exist_iki = request.args.get('iki', 'false').lower()
    
    stores_to_fetch = []
    if exist_rimi == 'true': stores_to_fetch.append('Rimi')
    if exist_iki == 'true': stores_to_fetch.append('Iki')

    if not stores_to_fetch:
        return jsonify([])

    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Naudojame IN operatorių, kad paimtume duomenis tik iš pasirinktų parduotuvių
        # Taip pat surūšiuojame pagal sukūrimo laiką, kad matytume naujausius skreipinimo rezultatus
        query = """
            SELECT name, price, image_url, protein, carbohydrates, fat, calories, store_name 
            FROM products 
            WHERE store_name = ANY(%s)
            ORDER BY id DESC
            LIMIT 100;
        """
        
        cursor.execute(query, (stores_to_fetch,))
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append({
                "name": row[0],
                "price": float(row[1]),
                "image": row[2],
                "baltymai": float(row[3] or 0),
                "angliavandeniai": float(row[4] or 0),
                "riebalai": float(row[5] or 0),
                "calories": float(row[6] or 0),
                "store": row[7],
                "storeLogo": f"[/static/Icons/](/static/Icons/){row[7].lower()}_logo.png"
            })
            
        return jsonify(data)
    
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