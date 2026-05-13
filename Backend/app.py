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
<<<<<<< HEAD
=======

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
                "storeLogo": f"[http://127.0.0.1:5000/static/Icons/](http://127.0.0.1:5000/static/Icons/){row[7].lower()}_logo.png"
            })
            
        return jsonify(data)
    
    except Exception as e:
        print(f"Klaida imant duomenis iš DB: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()
>>>>>>> b8b776b985a327ea66f885b3536e8e3818c90f4e

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
                "storeLogo": f"[http://127.0.0.1:5000/static/Icons/](http://127.0.0.1:5000/static/Icons/){row[7].lower()}_logo.png"
            })
            
        return jsonify(data)
    
    except Exception as e:
        print(f"Klaida imant duomenis iš DB: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()
 
 
@app.route('/api/search-address', methods=['GET'])
def search_address():
    query = request.args.get('q', '').strip()
    if len(query) < 3:
        return jsonify([])
 
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
 
        LT_FROM = 'ąčęėįšųūž'
        LT_TO   = 'aceeisuuz'
 
        # For address branches: %query% finds all matches (contains), but the CASE
        # scoring separates exact (1) → starts-with (2) → contains (3).
        # Sorting by score then by match_len puts "Bijūnų g. 12" above "Bijūnų g. 121".
        search_param = f"%{query}%"
 
        # For name-based branches: split the query into individual words and require
        # ALL of them (AND logic). This bypasses special chars like „ " that sit
        # between words in names such as PLC „Mega", so "plc mega" matches correctly.
        words = [w for w in query.split() if len(w) >= 2]
        if not words:
            words = [query]
 
        name_where = " AND ".join([
            f"translate(lower(name), '{LT_FROM}', '{LT_TO}') ILIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}')"
            for _ in words
        ])
        word_params = [f"%{w}%" for w in words]
 
        sql = f"""
            WITH scored AS (
 
                -- ADDRESS SEARCH: planet_osm_point
                SELECT
                    TRIM(addr_street || ' ' || addr_housenumber
                         || COALESCE(', ' || addr_city, '')) AS display_name,
                    ST_Y(way)                                 AS lat,
                    ST_X(way)                                 AS lon,
                    CASE
                        WHEN translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                             = translate(lower(%s), '{LT_FROM}', '{LT_TO}')             THEN 1
                        WHEN translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                             LIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}') || '%%' THEN 2
                        ELSE 3
                    END AS score,
                    length(addr_street || ' ' || addr_housenumber) AS match_len
                FROM planet_osm_point
                WHERE addr_street IS NOT NULL AND addr_housenumber IS NOT NULL
                  AND translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                      ILIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}')
 
                UNION ALL
 
                -- ADDRESS SEARCH: planet_osm_polygon
                SELECT
                    TRIM(addr_street || ' ' || addr_housenumber
                         || COALESCE(', ' || addr_city, '')) AS display_name,
                    ST_Y(ST_Centroid(way))                    AS lat,
                    ST_X(ST_Centroid(way))                    AS lon,
                    CASE
                        WHEN translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                             = translate(lower(%s), '{LT_FROM}', '{LT_TO}')             THEN 1
                        WHEN translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                             LIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}') || '%%' THEN 2
                        ELSE 3
                    END AS score,
                    length(addr_street || ' ' || addr_housenumber) AS match_len
                FROM planet_osm_polygon
                WHERE addr_street IS NOT NULL AND addr_housenumber IS NOT NULL
                  AND translate(lower(addr_street || ' ' || addr_housenumber), '{LT_FROM}', '{LT_TO}')
                      ILIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}')
 
                UNION ALL
 
                -- NAME SEARCH: planet_osm_polygon (Mega, Akropolis, etc.)
                SELECT
                    TRIM(name || COALESCE(', ' || addr_city, '')) AS display_name,
                    ST_Y(ST_Centroid(way))                         AS lat,
                    ST_X(ST_Centroid(way))                         AS lon,
                    CASE
                        WHEN translate(lower(name), '{LT_FROM}', '{LT_TO}')
                             = translate(lower(%s), '{LT_FROM}', '{LT_TO}')             THEN 1
                        WHEN translate(lower(name), '{LT_FROM}', '{LT_TO}')
                             LIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}') || '%%' THEN 2
                        ELSE 3
                    END AS score,
                    length(name) AS match_len
                FROM planet_osm_polygon
                WHERE name IS NOT NULL
                  AND (shop IS NOT NULL OR amenity IS NOT NULL OR building IS NOT NULL)
                  AND {name_where}
 
                UNION ALL
 
                -- NAME SEARCH: planet_osm_point (smaller shops / amenity nodes)
                SELECT
                    TRIM(name || COALESCE(', ' || addr_city, '')) AS display_name,
                    ST_Y(way)                                       AS lat,
                    ST_X(way)                                       AS lon,
                    CASE
                        WHEN translate(lower(name), '{LT_FROM}', '{LT_TO}')
                             = translate(lower(%s), '{LT_FROM}', '{LT_TO}')             THEN 1
                        WHEN translate(lower(name), '{LT_FROM}', '{LT_TO}')
                             LIKE translate(lower(%s), '{LT_FROM}', '{LT_TO}') || '%%' THEN 2
                        ELSE 3
                    END AS score,
                    length(name) AS match_len
                FROM planet_osm_point
                WHERE name IS NOT NULL
                  AND (shop IS NOT NULL OR amenity IS NOT NULL)
                  AND {name_where}
            )
            -- Inner DISTINCT ON keeps the best-scored row when the same display_name
            -- appears in both point and polygon tables.
            -- Outer ORDER BY then sorts all survivors by relevance.
            SELECT display_name, lat, lon
            FROM (
                SELECT DISTINCT ON (display_name)
                       display_name, lat, lon, score, match_len
                FROM scored
                WHERE display_name IS NOT NULL AND display_name <> ''
                ORDER BY display_name, score ASC, match_len ASC
            ) AS deduped
            ORDER BY score ASC, match_len ASC
            LIMIT 10;
        """
 
        # Parameter order matches %s placeholders above:
        #   address points  : query (CASE ×2) + search_param (WHERE ×1)
        #   address polygons: query (CASE ×2) + search_param (WHERE ×1)
        #   name polygons   : query (CASE ×2) + word_params  (WHERE, one per word)
        #   name points     : query (CASE ×2) + word_params  (WHERE, one per word)
        params = (
            query, query, search_param,
            query, query, search_param,
            query, query, *word_params,
            query, query, *word_params,
        )
 
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        results = [{"name": r[0], "lat": r[1], "lon": r[2]} for r in rows]
        return jsonify(results)
 
    except Exception as e:
        print(f"Klaida: {e}")
        return jsonify([])
    finally:
        if conn:
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
<<<<<<< HEAD
 
=======
>>>>>>> b8b776b985a327ea66f885b3536e8e3818c90f4e
    finally:
        if conn:
            cursor.close()
            conn.close()
 
 
if __name__ == '__main__':
    print("Flask serveris startuoja ant porto 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)