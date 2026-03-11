import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "API FredVertical Opérationnelle. Utilisez /get_car?plate=XX123YY"

@app.route('/get_car', methods=['GET'])
def get_car():
    plate = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    
    if not plate:
        return jsonify({"success": False, "error": "Plaque manquante"}), 400

    # On tente d'abord Oscaro, si ça échoue on pourra ajouter d'autres sources
    url = f"https://www.oscaro.com/catalog/vehicles/find?plate={plate}"
    
    try:
        # Configuration avancée du scraper pour éviter le blocage
        scraper = cloudscraper.create_scraper(
            delay=10, 
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            # Si Oscaro bloque, on renvoie une erreur explicite pour le debug
            return jsonify({"success": False, "error": f"Source bloquée (Code {response.status_code})"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraction du nom via la balise Title ou Meta
        title = soup.find('title').text if soup.find('title') else ""
        
        if "Oscaro" in title and "Pièces" not in title:
            return jsonify({"success": False, "error": "Véhicule non trouvé"}), 200

        car_name = title.replace("Pièces auto pour ", "").split("|")[0].strip()

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": plate,
            "year": 2018
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
