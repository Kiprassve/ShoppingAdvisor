import psycopg2
import os
import time

from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "map_demo")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password123")
DB_PORT = os.environ.get("DB_PORT", "5432")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def has_products():
    """Patikrina, ar produktų lentelėje jau yra duomenų (su retry logika)."""
    conn = None
    max_retries = 5       # Kiek kartų bandysime jungtis
    retry_delay = 3       # Kiek sekundžių lauksime tarp bandymų

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            
            # Patikriname, ar lentelė egzistuoja
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'products'
                );
            """)
            if not cursor.fetchone()[0]:
                return False

            # Skaičiuojame įrašus
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            return count > 0

        except psycopg2.OperationalError as e:
            # Jei tai prisijungimo klaida (pvz., Connection refused), palaukiame ir bandom vėl
            print(f"[{attempt + 1}/{max_retries}] DB dar nepasiruošusi ({e.args[0].splitlines()[0]}). Laukiama...")
            time.sleep(retry_delay)
        except Exception as e:
            # Jei tai kokia nors kita kritinė klaida, stabdom iškart
            print(f"Kritinė klaida tikrinant DB: {e}")
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
                
    # Jei po visų bandymų vis tiek nepavyko prisijungti:
    print("Nepavyko prisijungti prie DB po kelių bandymų. Saugumo sumetimais praleidžiame skreipinimą, kad neperkrautume sistemos.")
    return True  # Grąžiname True, kad crawleris nepradėtų skreipinti „į niekur“ (nes DB vis tiek neveikia)

def save_products_to_db(products, store_name):
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT,
                price NUMERIC,
                image_url TEXT,
                protein NUMERIC,
                carbohydrates NUMERIC,
                fat NUMERIC,
                calories NUMERIC,
                store_name TEXT,
                weight TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_store_name ON products(store_name);")

        # Išvalome senas tos parduotuvės prekes
        cursor.execute("DELETE FROM products WHERE store_name = %s", (store_name,))

        query = """
            INSERT INTO products (
                name, 
                price, 
                image_url, 
                protein, 
                carbohydrates, 
                fat, 
                calories, 
                store_name,
                weight
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for p in products:
            # Parenkame galiojančią kainą (prioritetas nuolaidai)[cite: 1, 2]
            current_price = str(p.price_discount if p.price_discount != "0" else p.price).replace(",", ".")
            
            def clean_float(val):
                if val == "0" or val is None:
                    return None
                try:
                    return float(str(val).replace(",", "."))
                except (ValueError, TypeError):
                    return None
            
            cursor.execute(query, (
                p.name,                        # 1. name
                float(current_price),          # 2. price
                p.image_url,                   # 3. image_url
                clean_float(p.protein),        # 4. protein
                clean_float(p.carbohydrates),  # 5. carbohydrates
                clean_float(p.fat),            # 6. fat
                clean_float(p.calories_kcal),  # 7. calories
                store_name, 
                clean_float(p.weight_kg),            # 8. store_name
            ))

        conn.commit()
        print(f"--- Sėkmingai išsaugota {len(products)} prekių iš {store_name} ---")
    except Exception as e:
        print(f"Klaida saugant į DB: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()