import socket
import time
import errno

H = 20
R = 50
HOST = "localhost"
PORT = 1024

def prey_process(shared_state, lock):
    energy = 40
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connexion à l'environnement
    while True:
        try:
            sock.connect((HOST, PORT))
            # On passe en mode non-bloquant après la connexion réussie
            sock.setblocking(False) 
            break
        except ConnectionRefusedError:
            print("[Prey] Waiting for ENV to be ready...")
            time.sleep(0.5)

    print("[Prey] Connected and running.")

    while energy > 0:
        # 1. Vérifier si l'environnement a envoyé un signal d'arrêt
        try:
            data = sock.recv(1024)
            if data == b"END":
                print("[Prey] Received END signal from environment. Stopping...")
                break
        except socket.error as e:
            # L'erreur EAGAIN ou EWOULDBLOCK signifie juste qu'il n'y a rien à lire
            err = e.args[0]
            if err != errno.EAGAIN and err != errno.EWOULDBLOCK:
                print(f"[Prey] Socket error: {e}")
                break

        # 2. Logique de survie
        energy -= 1

        # Choisir action
        if energy < H:
            with lock:
                if shared_state["grass"] > 0:
                    shared_state["grass"] -= 1
                    energy += 50
                    print(f"[Prey] ate grass, energy={energy}, grass left={shared_state['grass']}")

        # Reproduire si assez d'énergie
        elif energy > R:
            with lock:
                if shared_state["num_preys"] >= 2:
                    shared_state["num_preys"] += 1
                    energy -= 10
                    print(f"[Prey] reproduced, total preys={shared_state['num_preys']}")

        time.sleep(0.5)

    if energy <= 0:
        print("[Prey] Died of starvation.")
        # On décrémente le compteur si elle meurt naturellement
        with lock:
            if shared_state["num_preys"] > 0:
                shared_state["num_preys"] -= 1
    
    sock.close()
