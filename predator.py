import socket
import time
import errno

H = 30
R = 60
HOST = "localhost"
PORT = 1024

def predator_process(shared_state, lock):
    energy = 50
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 1. Connexion à l'environnement
    while True:
        try:
            sock.connect((HOST, PORT))
            # Passage en mode non-bloquant pour vérifier le signal END sans stopper la boucle
            sock.setblocking(False)
            break
        except ConnectionRefusedError:
            print("[Predator] Waiting for ENV to be ready...")
            time.sleep(0.5)

    print("[Predator] Connected and hunting.")

    while energy > 0:
        # 2. Vérification du signal d'arrêt de l'environnement (END)
        try:
            data = sock.recv(1024)
            if data == b"END":
                print("[Predator] Received END signal. Stopping simulation.")
                break
        except socket.error as e:
            # EAGAIN signifie qu'il n'y a pas de données pour le moment
            err = e.args[0]
            if err != errno.EAGAIN and err != errno.EWOULDBLOCK:
                print(f"[Predator] Socket error: {e}")
                break

        # 3. Logique de vie
        energy -= 1

        # Manger si faim
        if energy < H:
            with lock:
                if shared_state["num_preys"] > 0:
                    shared_state["num_preys"] -= 1
                    energy += 50
                    print(f"[Predator] ate a prey, energy={energy}, preys left={shared_state['num_preys']}")

        # Reproduire si assez d'énergie
        elif energy > R:
            with lock:
                if shared_state["num_predators"] >= 2:
                    shared_state["num_predators"] += 1
                    energy -= 15
                    print(f"[Predator] reproduced, total predators={shared_state['num_predators']}")

        time.sleep(0.5)

    # 4. Nettoyage et sortie
    if energy <= 0:
        print("[Predator] Died of starvation.")
        with lock:
            if shared_state["num_predators"] > 0:
                shared_state["num_predators"] -= 1
    
    sock.close()
