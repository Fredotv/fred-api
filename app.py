import os
import cloudscraper
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "API FredVertical (Source: PA24) active."

@app.route('/get_car', methods=['GET'])
def get_car():
    query = request.args.get('plate', '').replace("-", "").replace(" ", "").upper()
    
    if not query:
        return jsonify({"success": False, "error": "Saisie vide"}), 400

    # Source : Pièces Auto 24 (Plus stable pour le scraping)
    url = f"https://www.piecesauto24.com/rechercher?keyword={query}"
    
    try:
        # On utilise cloudscraper pour simuler un vrai visiteur
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Serveur distant indisponible ({response.status_code})"}), 200

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sur ce site, le nom du véhicule est souvent dans le titre ou un titre H1
        title_tag = soup.find('title')
        h1_tag = soup.find('h1')
        
        # On essaie d'extraire le nom propre
        raw_name = ""
        if title_tag:
            raw_name = title_tag.text.split('|')[0].strip()
        
        # Nettoyage pour ne pas afficher "Recherche" ou des mots inutiles
        if "recherche" in raw_name.lower() or len(raw_name) < 5:
            if h1_tag:
                raw_name = h1_tag.text.strip()

        # Si toujours rien de cohérent
        if not raw_name or "recherche" in raw_name.lower():
            return jsonify({"success": False, "error": "Véhicule non trouvé"}), 200

        return jsonify({
            "success": True,
            "name": raw_name.replace("Pièces auto pour ", ""),
            "plate": query,
            "type": "VIN" if len(query) == 17 else "PLAQUE",
            "year": 2018
        })

    except Exception as e:
        return jsonify({"success": False, "error": "Erreur de connexion"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
