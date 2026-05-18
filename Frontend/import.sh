#!/bin/bash
# import.sh — OSM duomenų importas su flex stiliumi į Docker PostgreSQL

# ============================================================
# Kintamieji — pakeisk pagal savo aplinką
# ============================================================

PBF_FILE="/osm/map_data.osm.pbf"        # .pbf failo pavadinimas
LUA_STYLE="/osm/kaunas.lua"             # flex stiliaus failas
DB_NAME="map_demo"                      # duomenų bazės pavadinimas
DB_USER="postgres"                 # PostgreSQL naudotojas
DB_HOST="db"                # arba Docker konteinerio IP/pavadinimas
DB_PORT="5432"

# ============================================================
# 1. Prieš importą: įsitikink, kad PostGIS ir hstore įjungti
# ============================================================

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS hstore;
"

# ============================================================
# 2. Pagrindinis importas su flex stiliumi
# ============================================================

osm2pgsql \
    --database $DB_NAME \
    --host $DB_HOST \
    --port $DB_PORT \
    --user $DB_USER \
    --slim \
    --drop \
    --output=flex \
    --style=$LUA_STYLE \
    --number-processes=4 \
    $PBF_FILE

# --slim        : naudoja tarpines lenteles (reikalinga dideliam failui)
# --drop        : po importo ištrina tarpines lenteles (taupo vietą)
# --output=flex : nurodo naudoti flex stilių (ne senąjį pgsql)
# --style       : nurodo .lua konfigūracijos failą
# --number-processes : lygiagretūs procesai (pakeisk pagal CPU skaičių)

# ============================================================
# 3. Indeksų sukūrimas adresų paieškai (po importo)
# ============================================================

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
    -- Indeksai greičiausiai paieškai
    CREATE INDEX IF NOT EXISTS idx_point_addr_street
        ON planet_osm_point (addr_street);

    CREATE INDEX IF NOT EXISTS idx_point_addr_housenumber
        ON planet_osm_point (addr_housenumber);

    CREATE INDEX IF NOT EXISTS idx_polygon_addr_street
        ON planet_osm_polygon (addr_street);

    CREATE INDEX IF NOT EXISTS idx_polygon_addr_housenumber
        ON planet_osm_polygon (addr_housenumber);

    -- Kombinuotas indeksas efektyvesnei paieškai
    CREATE INDEX IF NOT EXISTS idx_point_full_address
        ON planet_osm_point (addr_street, addr_housenumber);

    CREATE INDEX IF NOT EXISTS idx_polygon_full_address
        ON planet_osm_polygon (addr_street, addr_housenumber);

    -- GiST geometrijos indeksas (jei dar nėra)
    CREATE INDEX IF NOT EXISTS idx_point_way
        ON planet_osm_point USING GIST (way);

    CREATE INDEX IF NOT EXISTS idx_polygon_way
        ON planet_osm_polygon USING GIST (way);
"

echo "✅ Importas baigtas. Lentelės planet_osm_point ir planet_osm_polygon sukurtos."

# ============================================================
# Docker aplinkoje (jei osm2pgsql paleidžiamas konteineryje):
# ============================================================
#
# docker run --rm \
#     -v $(pwd):/data \
#     --network host \
#     iboates/osm2pgsql:latest \
#     osm2pgsql \
#         --database gis \
#         --host localhost \
#         --port 5432 \
#         --user postgres \
#         --slim --drop \
#         --output=flex \
#         --style=/data/kaunas.lua \
#         --number-processes=4 \
#         /data/map_data_osm.pbf
