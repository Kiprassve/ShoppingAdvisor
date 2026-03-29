from flask import Flask, jsonify
from flask_cors import CORS
from Crawler.Crawler.Crawler import Rimi_crawler # Jūsų crawlerio funkcija

app = Flask(__name__)
CORS(app) # Leidžia jūsų puslapiui susisiekti su šiuo serveriu

@app.route('/api/scrape', methods=['GET'])
def get_data():
    url = "https://www.rimi.lt/e-parduotuve/lt/produktai/mesa-ir-zuvis-/c/SH-9?currentPage=1&pageSize=80"
    
    # Paleidžiame crawlerį
    products_objects = Rimi_crawler(url, max_pages=1, item_limit=10)
    
    data = []
    for p in products_objects:
        try:
            # Pagal tavo Product.py failą:
            # p.carbohydrates, o ne p.carbs
            # p.image_url, o ne p.img_url
            # p.calories_kcal, o ne p.calories
            
            data.append({
                "name": p.name,
                "price": 0.0, 
                "image": p.image_url,
                "baltymai": float(str(p.protein).replace(',', '.')),
                "angliavandeniai": float(str(p.carbohydrates).replace(',', '.')),
                "riebalai": float(str(p.fat).replace(',', '.')),
                "store": "Rimi",
                "storeLogo": "Icons/rimi_logo.png"
            })
        except Exception as e:
            print(f"Klaida su produktu {p.name}: {e}")
            continue
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)