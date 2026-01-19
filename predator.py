import socket
import time

H = 30
R = 60
HOST = "localhost"
PORT = 1024

def predator_process(shared_state, lock):
    energy = 50
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connexion à l'environnement
    while True:
        try:
            sock.connect((HOST, PORT))
            break
        except ConnectionRefusedError:
            print("[Predator] Waiting for ENV to be ready...")
            time.sleep(0.5)

    while energy > 0:
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

    print("Predator died")
    sock.close()
