import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/get_car', methods=['GET'])
def get_car():
    query = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    if not query:
        return jsonify({"success": False, "error": "Saisie vide"}), 400

    # On utilise le moteur de recherche international d'Auto-Doc
    # C'est souvent moins bloqué que les versions .fr
    url = f"https://www.autodoc.de/search?keyword={query}"
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Accès refusé ({response.status_code})"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        
        if not title_tag or "Suche" in title_tag.text:
             return jsonify({"success": False, "error": "Véhicule non répertorié"}), 200

        # On nettoie le nom (qui sera peut-être en allemand, ex: "Ersatzteile für...")
        name = title_tag.text.split('|')[0].replace("Ersatzteile für", "").replace("Autoteile", "").strip()

        return jsonify({
            "success": True,
            "name": name,
            "plate": query,
            "year": 2019
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur réseau"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
