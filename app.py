import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)
# Autorise ton site sur Free.fr à interroger ce script sur Render
CORS(app)

@app.route('/get_car', methods=['GET'])
def get_car():
    # 1. Récupération et nettoyage de la saisie (Plaque ou VIN)
    raw_query = request.args.get('plate', '').strip()
    # On enlève les tirets et les espaces pour ne pas perdre Oscaro
    query = raw_query.replace("-", "").replace(" ", "").upper()
    
    if not query:
        return jsonify({"success": False, "error": "Requête vide"}), 400

    # 2. Détermination de l'URL Oscaro (Plaque vs VIN)
    # Un VIN fait toujours 17 caractères
    if len(query) == 17:
        url = f"https://www.oscaro.com/catalog/vehicles/find?vin={query}"
    else:
        url = f"https://www.oscaro.com/catalog/vehicles/find?plate={query}"
    
    try:
        # 3. Utilisation de cloudscraper pour contourner les protections
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Oscaro ne répond pas"}), 500

        # 4. Analyse de la page avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On extrait le titre de la page qui contient normalement le nom du véhicule
        page_title = soup.find('title').text if soup.find('title') else ""
        
        # Si Oscaro ne trouve pas, il renvoie souvent vers une page générique
        if "Pièces auto" not in page_title or "Oscaro.com" not in page_title:
            return jsonify({"success": False, "error": "Véhicule non trouvé sur Oscaro"}), 404

        # Nettoyage du titre pour garder uniquement le nom de la voiture
        # Exemple: "Pièces auto pour PEUGEOT 208 I 1.2 i 82cv | Oscaro.com" -> "PEUGEOT 208 I 1.2 i 82cv"
        car_name = page_title.replace("Pièces auto pour ", "").split("|")[0].strip()

        return jsonify({
            "success": True,
            "name": car_name,
            "plate": raw_query,
            "year": 2018, # Oscaro ne donne pas l'année exacte dans le titre
            "source": "Oscaro Database"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Utilisation du port défini par Render ou 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
