from flask import Flask, request, jsonify, send_from_directory
import json
import os
import random
import string

app = Flask(__name__, static_folder='.', static_url_path='')

DATA_FILE = 'torneos.json'

def load_tournaments():
    """Carga los torneos desde el archivo JSON o crea uno vacío si no existe."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_tournaments(data):
    """Guarda los torneos en el archivo JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/tournaments', methods=['POST'])
def save_tournament():
    try:
        data = request.json
        tournaments_db = load_tournaments()
        
        # Si el torneo no tiene código aún, le generamos uno (ej. FC-A1B2)
        if 'shareCode' not in data or not data['shareCode']:
            while True:
                code = 'FC-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                if code not in tournaments_db:
                    data['shareCode'] = code
                    break
        
        code = data['shareCode']
        tournaments_db[code] = data
        save_tournaments(tournaments_db)
        
        return jsonify({"success": True, "shareCode": code})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/tournaments/<code>', methods=['GET'])
def get_tournament(code):
    tournaments_db = load_tournaments()
    if code in tournaments_db:
        return jsonify({"success": True, "tournament": tournaments_db[code]})
    return jsonify({"success": False, "message": "Torneo no encontrado"}), 404

if __name__ == '__main__':
    # Usamos el puerto asignado por Render (o 5000 por defecto)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
