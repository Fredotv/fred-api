import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "API FredVertical (Source PA24) active."

@app.route('/get_car', methods=['GET'])
def get_car():
    query = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    
    if not query:
        return jsonify({"success": False, "error": "Saisie vide"}), 400

    # Utilisation de PiecesAuto24 qui est plus ouvert au SIV/VIN
    url = f"https://www.piecesauto24.com/rechercher?keyword={query}"
    
    try:
        # On simule un navigateur très récent
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Source indisponible ({response.status_code})"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sur PA24, le nom du véhicule est dans le titre de la page
        title_tag = soup.find('title')
        if not title_tag:
             return jsonify({"success": False, "error": "Données illisibles"}), 200

        full_title = title_tag.text
        
        # Si on est sur une page de résultats, le titre contient le nom de la voiture
        # On nettoie les textes inutiles
        car_name = full_title.split('|')[0].replace("Pièces auto pour", "").replace("Catalogues de pièces détachées pour", "").strip()

        if "recherche" in car_name.lower() or len(car_name) < 5:
            return jsonify({"success": False, "error": "Véhicule non trouvé dans cette base"}), 200

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": query,
            "source": "PA24 Database"
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur de connexion réseau"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
