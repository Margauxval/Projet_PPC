import socket
import time

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
            break
        except ConnectionRefusedError:
            print("[Prey] Waiting for ENV to be ready...")
            time.sleep(0.5)

    while energy > 0:
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

    print("Prey died")
    sock.close()
