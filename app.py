import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import random

app = Flask(__name__)
CORS(app)

# Liste de faux navigateurs pour tromper les protections
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

@app.route('/')
def index():
    return "API FredVertical v3 (Multi-Source) Active."

@app.route('/get_car', methods=['GET'])
def get_car():
    query = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    if not query:
        return jsonify({"success": False, "error": "Saisie vide"}), 400

    # On tente une recherche via un portail de recherche plus permissif
    url = f"https://www.auto-doc.fr/search?keyword={query}"
    
    try:
        # On crée un scraper qui change d'identité à chaque fois
        scraper = cloudscraper.create_scraper(
            delay=10,
            browser={
                'custom_agent': random.choice(USER_AGENTS),
            }
        )
        
        response = scraper.get(url, timeout=15)
        
        # Si ça bloque encore (403), on tente une source de secours ultra-légère
        if response.status_code == 403:
            # Source de secours : Euro de l'Auto ou similaire
            url = f"https://www.pluspiecesauto.com/recherche?search_query={query}"
            response = scraper.get(url, timeout=10)

        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Bases de données saturées (Code {response.status_code})"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        
        if not title_tag or "recherche" in title_tag.text.lower() and len(title_tag.text) < 20:
             return jsonify({"success": False, "error": "Véhicule introuvable dans nos bases"}), 200

        # Nettoyage du nom
        name = title_tag.text.split('|')[0].replace("Pièces auto pour", "").replace("Auto-doc", "").strip()

        return jsonify({
            "success": True,
            "name": name,
            "plate": query,
            "year": 2018
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur de connexion réseau"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
