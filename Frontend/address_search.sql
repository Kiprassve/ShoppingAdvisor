-- address_search.sql
-- SQL užklausos adresų paieškai planet_osm_point ir planet_osm_polygon lentelėse
-- Suderintos su osm2pgsql flex stiliumi (addr_street, addr_housenumber stulpeliai)

-- ============================================================
-- 1. TIKSLUS adreso paieška (pvz.: "Raudondvario pl. 169B")
-- ============================================================

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    addr_postcode,
    ST_Y(way) AS latitude,
    ST_X(way) AS longitude,
    'point' AS source
FROM planet_osm_point
WHERE
    addr_street      = 'Raudondvario pl.'
    AND addr_housenumber = '169B'

UNION ALL

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    addr_postcode,
    ST_Y(ST_Centroid(way)) AS latitude,
    ST_X(ST_Centroid(way)) AS longitude,
    'polygon' AS source
FROM planet_osm_polygon
WHERE
    addr_street      = 'Raudondvario pl.'
    AND addr_housenumber = '169B';


-- ============================================================
-- 2. LAISVAS paieška (dalinė eilutė, case-insensitive)
--    Tinka kai nežinai tikslaus formato
-- ============================================================

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    ST_Y(way) AS latitude,
    ST_X(way) AS longitude,
    'point' AS source
FROM planet_osm_point
WHERE
    addr_street      ILIKE '%Raudondvario%'
    AND addr_housenumber ILIKE '%169B%'

UNION ALL

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    ST_Y(ST_Centroid(way)) AS latitude,
    ST_X(ST_Centroid(way)) AS longitude,
    'polygon' AS source
FROM planet_osm_polygon
WHERE
    addr_street      ILIKE '%Raudondvario%'
    AND addr_housenumber ILIKE '%169B%';


-- ============================================================
-- 3. KOMBINUOTA eilutė — vienas laukas "pilnas adresas"
--    Tinka kai programa gauna vieną adreso eilutę iš vartotojo
-- ============================================================

-- Sukurti view su sujungtu adresu (patogu pakartotinai naudoti):
CREATE OR REPLACE VIEW v_full_address AS
SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    addr_postcode,
    -- Sujungiame į vieną eilutę: "Raudondvario pl. 169B"
    TRIM(CONCAT_WS(' ', addr_street, addr_housenumber)) AS full_address,
    way,
    ST_Y(way) AS latitude,
    ST_X(way) AS longitude,
    'point' AS geom_type
FROM planet_osm_point
WHERE addr_street IS NOT NULL

UNION ALL

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    addr_postcode,
    TRIM(CONCAT_WS(' ', addr_street, addr_housenumber)) AS full_address,
    ST_Centroid(way) AS way,
    ST_Y(ST_Centroid(way)) AS latitude,
    ST_X(ST_Centroid(way)) AS longitude,
    'polygon' AS geom_type
FROM planet_osm_polygon
WHERE addr_street IS NOT NULL;

-- Paieška per view:
SELECT * FROM v_full_address
WHERE full_address ILIKE '%Raudondvario pl. 169B%';


-- ============================================================
-- 4. PREKYBOS CENTRO paieška pagal pavadinimą (pvz.: "Mega")
-- ============================================================

SELECT
    osm_id,
    name,
    addr_street,
    addr_housenumber,
    addr_city,
    shop,
    ST_Y(ST_Centroid(way)) AS latitude,
    ST_X(ST_Centroid(way)) AS longitude
FROM planet_osm_polygon
WHERE
    name ILIKE '%Mega%'
    AND (shop IS NOT NULL OR amenity IS NOT NULL)
ORDER BY name;


-- ============================================================
-- 5. Python (psycopg2) pavyzdys su parametrizuota užklausa
--    (apsauga nuo SQL injection)
-- ============================================================

/*
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="gis",
    user="postgres",
    password="slaptazodis"
)
cur = conn.cursor()

# Tikslus adreso paieška
cur.execute("""
    SELECT osm_id, name, addr_street, addr_housenumber,
           ST_Y(way) AS lat, ST_X(way) AS lon
    FROM planet_osm_point
    WHERE addr_street = %s AND addr_housenumber = %s

    UNION ALL

    SELECT osm_id, name, addr_street, addr_housenumber,
           ST_Y(ST_Centroid(way)) AS lat,
           ST_X(ST_Centroid(way)) AS lon
    FROM planet_osm_polygon
    WHERE addr_street = %s AND addr_housenumber = %s
    LIMIT 10
""", ('Raudondvario pl.', '169B', 'Raudondvario pl.', '169B'))

results = cur.fetchall()
for row in results:
    print(row)

cur.close()
conn.close()
*/


-- ============================================================
-- 6. Patikrinimas po importo — ar stulpeliai egzistuoja?
-- ============================================================

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('planet_osm_point', 'planet_osm_polygon')
  AND column_name LIKE 'addr%'
ORDER BY table_name, column_name;
