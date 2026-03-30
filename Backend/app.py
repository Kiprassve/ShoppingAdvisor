from flask import Flask, jsonify
from flask_cors import CORS
from Crawler.Crawler.Crawler import Rimi_crawler

app = Flask(__name__, static_folder='static')
CORS(app)

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

# SVARBU: Įsitikink, kad virš šios eilutės NĖRA jokio kito Rimi_crawler(url) kvietimo!
if __name__ == '__main__':
    print("Flask serveris startuoja ant porto 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)