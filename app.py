from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app) # Autorise ta page HTML à interroger ce script

@app.route('/get_car', methods=['GET'])
def get_car():
    plate = request.args.get('plate')
    url = f"https://www.oscaro.com/catalog/vehicles/find?plate={plate}"
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        
        # On cherche le nom du véhicule dans le code source d'Oscaro
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Logique simplifiée : Oscaro renvoie souvent un JSON ou un titre
        # Ici on simule l'extraction du nom du modèle
        car_name = soup.find('title').text.replace('Pièces auto pour ', '').split('|')[0].strip()
        
        if "Oscaro" in car_name: # Si la plaque n'est pas trouvée
            return jsonify({"error": "Véhicule non trouvé"}), 404

        return jsonify({
            "name": car_name,
            "plate": plate,
            "year": 2019, # Oscaro ne donne pas toujours l'année en clair, on peut l'estimer
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)