from flask import Flask, request, jsonify # type: ignore
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
@app.route('/execute', methods=['ANY'])
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
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Serveur</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                text-align: center;
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
            }
            p {
                color: #666;
            }
            .credits {
                margin-top: 20px;
                font-size: 0.9em;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bienvenue sur l'API Serveur</h1>
            <p>Utilisez l'endpoint <code>/execute</code> pour exécuter des commandes shell.</p>
            <div class="credits">
                <p>Contributeurs : William Meunier, Maxime Abade, Gustave Richter</p>
            </div>
        </div>
    </body>
    </html>
    """

# Listener pour capturer les commandes exécutées
def log_command(command):
    print(f"Nouvelle commande exécutée : {command}")

command_event.subscribe(log_command)

# Lancer le serveur Flask
if __name__ == '__main__':
    print(f"Serveur en écoute sur http://localhost:{PORT}")
    app.run(debug=True, port=PORT)
