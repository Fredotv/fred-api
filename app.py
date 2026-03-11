import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "API FredVertical SIV/VIN active."

@app.route('/get_car', methods=['GET'])
def get_car():
    # Nettoyage de l'entrée (Plaque ou VIN)
    query = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    
    if not query:
        return jsonify({"success": False, "error": "Saisie vide"}), 400

    # CHOIX DE LA PORTE : Si 17 caractères = VIN, sinon = PLAQUE
    if len(query) == 17:
        url = f"https://www.oscaro.com/fr/search?vin={query}"
        type_search = "VIN"
    else:
        url = f"https://www.oscaro.com/fr/search?plate={query}"
        type_search = "PLAQUE"
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        response = scraper.get(url, timeout=15)
        
        # Si Oscaro redirige ou ne trouve pas
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Erreur Oscaro {response.status_code}"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        
        if not title_tag or "Oscaro.com" not in title_tag.text:
            return jsonify({"success": False, "error": f"{type_search} non reconnu par Oscaro"}), 200

        car_name = title_tag.text.replace("Pièces auto pour ", "").split("|")[0].strip()

        # Si le titre est juste "Oscaro", c'est un échec de recherche
        if car_name.lower() == "oscaro" or len(car_name) < 5:
             return jsonify({"success": False, "error": f"{type_search} introuvable"}), 200

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": query,
            "type": type_search,
            "year": 2018
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur technique"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
