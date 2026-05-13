-- kaunas.lua
-- Versija skirta osm2pgsql 1.6.0 (Flex stilius)
-- PATAISYTA: process_way ir process_relation gauna `row.way = { create = 'area' }`
-- kad geometrija būtų sukurta teisingai be object:as_polygon() (1.7+ sintaksė).
 
local tables = {}
 
-- ============================================================
-- Lentelių apibrėžimas
-- ============================================================
 
-- Taškiniai objektai (nodes) — geometrija čia automatinė (define_node_table).
tables.osm_point = osm2pgsql.define_node_table('planet_osm_point', {
    { column = 'osm_id',           type = 'int8' },
    { column = 'name',             type = 'text' },
    { column = 'addr_street',      type = 'text' },
    { column = 'addr_housenumber', type = 'text' },
    { column = 'addr_city',        type = 'text' },
    { column = 'addr_postcode',    type = 'text' },
    { column = 'amenity',          type = 'text' },
    { column = 'shop',             type = 'text' },
    { column = 'highway',          type = 'text' },
    { column = 'building',         type = 'text' },
    { column = 'tags',             type = 'hstore' },
    { column = 'way',              type = 'point', projection = 4326, not_null = true },
})
 
-- Poligoniniai objektai (ways + relations) — geometrija turi būti nurodyta
-- EKSPLICITIŠKAI per { create = 'area' } (1.6.0 reikalavimas).
tables.osm_polygon = osm2pgsql.define_area_table('planet_osm_polygon', {
    { column = 'osm_id',           type = 'int8' },
    { column = 'name',             type = 'text' },
    { column = 'addr_street',      type = 'text' },
    { column = 'addr_housenumber', type = 'text' },
    { column = 'addr_city',        type = 'text' },
    { column = 'addr_postcode',    type = 'text' },
    { column = 'amenity',          type = 'text' },
    { column = 'shop',             type = 'text' },
    { column = 'building',         type = 'text' },
    { column = 'landuse',          type = 'text' },
    { column = 'leisure',          type = 'text' },
    { column = 'tags',             type = 'hstore' },
    { column = 'way',              type = 'geometry', projection = 4326, not_null = true },
})
 
-- ============================================================
-- Pagalbinė funkcija — bendra visoms lentelėms
-- ============================================================
 
local function get_address_fields(object)
    return {
        osm_id           = object.id,
        name             = object:grab_tag('name'),
        addr_street      = object:grab_tag('addr:street'),
        addr_housenumber = object:grab_tag('addr:housenumber'),
        addr_city        = object:grab_tag('addr:city'),
        addr_postcode    = object:grab_tag('addr:postcode'),
        amenity          = object:grab_tag('amenity'),
        shop             = object:grab_tag('shop'),
        building         = object:grab_tag('building'),
    }
end
 
-- ============================================================
-- Nodes — define_node_table tvarko geometriją automatiškai.
-- Nereikia nustatyti row.way rankiniu būdu.
-- ============================================================
 
function osm2pgsql.process_node(object)
    local tags = object.tags
    if not (tags['addr:street'] or tags['addr:housenumber'] or
            tags['name'] or tags['amenity'] or tags['shop'] or
            tags['highway']) then
        return
    end
 
    local row = get_address_fields(object)
    row.highway = object:grab_tag('highway')
    row.tags    = object.tags
 
    -- Geometrija (taškas) priskiriama automatiškai iš node koordinačių.
    tables.osm_point:add_row(row)
end
 
-- ============================================================
-- Ways — FIX: row.way = { create = 'area' }
--
-- Tai yra 1.6.0 Flex stiliaus geometrijos transformacijos sintaksė.
-- Ji liepia osm2pgsql sukurti poligoną iš uždaro way.
-- NENAUDOKITE object:as_polygon() — tai 1.7+ sintaksė.
-- ============================================================
 
function osm2pgsql.process_way(object)
    -- Ignoruojame atvirus (ne uždarus) kelius — jie negali tapti poligonais.
    if not object.is_closed then
        return
    end
 
    local tags = object.tags
    if not (tags['building'] or tags['landuse'] or tags['leisure'] or
            tags['amenity'] or tags['shop'] or tags['addr:street'] or
            tags['addr:housenumber']) then
        return
    end
 
    local row = get_address_fields(object)
    row.landuse = object:grab_tag('landuse')
    row.leisure = object:grab_tag('leisure')
    row.tags    = object.tags
 
    -- PATAISYMAS: Eksplicitiškai nurodome geometrijos transformaciją.
    -- { create = 'area' } yra 1.6.0 Flex stiliaus sintaksė poligonui kurti.
    row.way = { create = 'area' }
 
    tables.osm_polygon:add_row(row)
end
 
-- ============================================================
-- Relations — FIX: row.way = { create = 'area' }
--
-- Multipolygon ir boundary reliacijos taip pat reikalauja
-- eksplicitinės geometrijos transformacijos 1.6.0 versijoje.
-- ============================================================
 
function osm2pgsql.process_relation(object)
    local tags = object.tags
 
    -- Apdorojame tik multipolygon ir boundary reliacijas.
    if tags['type'] ~= 'multipolygon' and tags['type'] ~= 'boundary' then
        return
    end
 
    if not (tags['building'] or tags['landuse'] or tags['amenity'] or
            tags['shop'] or tags['addr:street']) then
        return
    end
 
    local row = get_address_fields(object)
    row.landuse = object:grab_tag('landuse')
    row.leisure = object:grab_tag('leisure')
    row.tags    = object.tags
 
    -- PATAISYMAS: Tas pats kaip process_way — reikalinga eksplicitinė
    -- geometrijos transformacija multipolygon relationams.
    row.way = { create = 'area' }
 
    tables.osm_polygon:add_row(row)
end