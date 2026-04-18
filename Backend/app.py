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
    # URL kintamasis turi būti ČIA, funkcijos viduje
    url = "https://www.rimi.lt/e-parduotuve/lt/produktai/mesa-ir-zuvis-/c/SH-9?currentPage=1&pageSize=80"
    
    print("Pradedamas skreipinimas...")
    products_objects = Rimi_crawler(url)
    
    data = []
    for p in products_objects:
        try:
            # Tavo esama logika su kainomis ir baltymais...
            p_discount = str(p.price_discount).replace(',', '.').strip()
            p_price = str(p.price).replace(',', '.').strip()
            
            if p_discount != "0" and p_discount != "":
                final_price = float(p_discount)
            else:
                final_price = float(p_price)

            data.append({
                "name": p.name,
                "price": final_price,
                "image": p.image_url,
                "baltymai": float(str(p.protein).replace(',', '.')),
                "angliavandeniai": float(str(p.carbohydrates).replace(',', '.')),
                "riebalai": float(str(p.fat).replace(',', '.')),
                "calories": float(p.calories_kcal),
                "store": "Rimi",
                "storeLogo": "http://127.0.0.1:5000/static/Icons/rimi_logo.png"
            })
        except Exception as e:
            continue
            
    return jsonify(data)

@app.route('/api/stores', methods=['GET'])
def get_stores():
    # 1. Get coordinates and radius from Leaflet
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', type=float)

    if not all([lat, lon, radius]):
        return jsonify({"error": "Missing lat, lon, or radius"}), 400

    conn = None
    try:
        
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
       
        sql = """
            SELECT 
            name, 
                ST_Y(ST_Transform(way, 4326)) as lat, 
                ST_X(ST_Transform(way, 4326)) as lon 
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
                ST_X(ST_Transform(ST_Centroid(way), 4326)) as lon 
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
                "name": row[0] if row[0] else "Unnamed Store",
                "lat": row[1],
                "lon": row[2]
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