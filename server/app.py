from flask import Flask, request, jsonify
import subprocess
import os
import threading

# Création de l'application Flask
app = Flask(__name__)
PORT = 3000

# Gestionnaire d'événements pour les commandes
class CommandEvent:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def emit(self, command):
        for callback in self.subscribers:
            callback(command)

command_event = CommandEvent()
# Route POST pour exécuter des commandes shell
@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
        
    if not data or "command" not in data:
        return jsonify({"error": "Aucune commande fournie."}), 400

    command = data["command"]

    # Émission de l'événement pour la commande
    threading.Thread(target=command_event.emit, args=(command,)).start()

    # Exécution de la commande shell
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=os.getcwd())
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500

# Route GET pour la racine "/"
@app.route('/')
def home():
    return """
    <h1>Bienvenue sur l'API Serveur</h1>
    """

# Listener pour capturer les commandes exécutées
def log_command(command):
    print(f"Nouvelle commande exécutée : {command}")

command_event.subscribe(log_command)

# Lancer le serveur Flask
if __name__ == '__main__':
    print(f"Serveur en écoute sur http://localhost:{PORT}")
    app.run(debug=True, port=PORT)
