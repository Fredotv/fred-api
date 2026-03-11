import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/get_car', methods=['GET'])
def get_car():
    # Nettoyage de la plaque
    raw_query = request.args.get('plate', '').strip()
    query = raw_query.replace("-", "").replace(" ", "").upper()
    
    if not query:
        return jsonify({"success": False, "error": "Plaque vide"}), 400

    # URL Oscaro
    if len(query) == 17:
        url = f"https://www.oscaro.com/catalog/vehicles/find?vin={query}"
    else:
        url = f"https://www.oscaro.com/catalog/vehicles/find?plate={query}"
    
    try:
        # Configuration d'un scraper plus "humain"
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # On fait la requête
        response = scraper.get(url, timeout=20)
        
        # Si Oscaro nous bloque (403), on essaie une autre méthode
        if response.status_code != 200:
             return jsonify({"success": False, "error": f"Oscaro bloque (Code {response.status_code})"}), 403

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- NOUVELLE LOGIQUE D'EXTRACTION ---
        # 1. On cherche d'abord dans les balises meta (plus fiable)
        meta_desc = soup.find("meta", property="og:title")
        if meta_desc:
            car_name = meta_desc["content"]
        else:
            car_name = soup.find('title').text if soup.find('title') else ""

        # Nettoyage strict
        car_name = car_name.replace("Pièces auto pour ", "").split("|")[0].split(" - Oscaro")[0].strip()

        # Si le nom contient encore "Oscaro" ou est trop court, c'est un échec
        if "Oscaro" in car_name or len(car_name) < 5:
            return jsonify({"success": False, "error": "Véhicule non trouvé"}), 404

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": raw_query,
            "year": 2017, # Valeur par défaut
            "status": "Identification OK"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
