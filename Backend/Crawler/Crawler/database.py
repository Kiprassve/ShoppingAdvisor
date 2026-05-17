import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "map_demo")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password123")
DB_PORT = os.environ.get("DB_PORT", "5432")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


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
                store_name TEXT
            );
        """)

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
                store_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                store_name                     # 8. store_name
            ))

        conn.commit()
        print(f"--- Sėkmingai išsaugota {len(products)} prekių iš {store_name} ---")
    except Exception as e:
        print(f"Klaida saugant į DB: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()