import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "API FredVertical v5 (VIN Only) Active."

@app.route('/get_car', methods=['GET'])
def get_car():
    # On récupère le paramètre envoyé par le HTML
    vin = request.args.get('plate', '').replace(" ", "").upper()
    
    if len(vin) != 17:
        return jsonify({"success": False, "error": "Le VIN doit faire 17 caractères"}), 400

    # Source : Auto-Doc (Moteur de recherche par VIN)
    url = f"https://www.auto-doc.fr/search?keyword={vin}"
    
    try:
        # Utilisation de cloudscraper pour contourner les protections anti-robot
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        response = scraper.get(url, timeout=15)
        
        if response.status_code == 403:
            return jsonify({"success": False, "error": "Accès refusé par la base (403). Réessayez plus tard."}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On extrait le nom du véhicule depuis le titre de la page
        title_tag = soup.find('title')
        if not title_tag:
            return jsonify({"success": False, "error": "Données illisibles"}), 200

        full_title = title_tag.text
        # Nettoyage du titre pour garder uniquement le modèle
        car_name = full_title.split('|')[0].replace("Pièces auto pour", "").replace("Auto-doc", "").strip()

        # Si le site ne trouve rien, il affiche souvent sa propre page de recherche
        if "recherche" in car_name.lower() or len(car_name) < 5:
            return jsonify({"success": False, "error": "VIN non répertorié"}), 200

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": vin
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur technique"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
