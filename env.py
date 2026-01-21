import socket
import time
from multiprocessing import Manager, Lock, Queue

HOST = "localhost"
PORT = 1024

def env_process(shared_state, msg_queue, lock):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("[ENV] Waiting for clients...")

    clients = []
    while len(clients) < 2:  
        client_sock, addr = server.accept()
        clients.append(client_sock)
        print(f"[ENV] Client connected: {addr}")

    print("[ENV] All clients connected, starting simulation")

    try:
        while True:
            # Croissance de l'herbe
            with lock:
                shared_state["grass"] += 1
                state_str = f"Grass={shared_state['grass']} | Preys={shared_state['num_preys']} | Predators={shared_state['num_predators']}"
                msg_queue.put(state_str)

                # Condition d'arrêt
                if shared_state["num_preys"] <= 0 or shared_state["num_predators"] <= 0:
                    print("[ENV] No preys or predators left. Ending simulation.")
                    
                    # 1. Prévenir les clients
                    for client in clients:
                        try:
                            client.sendall(b"END")
                        except Exception:
                            pass 

                    # 2. TEMPS MORT : Très important pour laisser les clients recevoir b"END"
                    time.sleep(1) 

                    # 3. Stopper l'affichage et sortir
                    msg_queue.put("STOP")
                    return

            time.sleep(1)
    finally:
        # Fermer tous les clients et le serveur proprement
        for client in clients:
            try:
                client.close()
            except Exception:
                pass
        server.close()
        # Sécurité : on s'assure que le message STOP est bien envoyé
        msg_queue.put("STOP")



####
2e version de env.py
###

import socket
import time

HOST = "localhost"
PORT = 1024

def env_process(shared_state, msg_queue, lock):
    paused = False

    # --- serveur ---
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[ENV] Waiting for clients...")

    clients = []
    while len(clients) < 2:
        client, addr = server.accept()
        clients.append(client)
        print(f"[ENV] Client connected: {addr}")

    print("[ENV] All clients connected, starting simulation")

    # --- boucle principale ---
    while True:

        # 1️⃣ lire commandes display
        while not msg_queue.empty():
            msg = msg_queue.get()

            if isinstance(msg, tuple) and msg[0] == "CMD":
                if msg[1] == "PAUSE":
                    paused = True
                    print("[ENV] Paused")
                elif msg[1] == "RESUME":
                    paused = False
                    print("[ENV] Resumed")
                elif msg[1] == "DROUGHT":
                    shared_state["drought"] = True
                elif msg[1] == "STOP":
                    msg_queue.put("STOP")
                    return

        # 2️⃣ pause réelle
        if paused:
            time.sleep(0.2)
            continue   # ⬅️ C’EST ÇA QUI BLOQUAIT AVANT

        # 3️⃣ simulation normale
        with lock:
            if not shared_state.get("drought", False):
                shared_state["grass"] += 1

            state = (
                f"Grass={shared_state['grass']} | "
                f"Preys={shared_state['num_preys']} | "
                f"Predators={shared_state['num_predators']}"
            )

            msg_queue.put(state)

            # condition d'arrêt
            if shared_state["num_preys"] <= 0 or shared_state["num_predators"] <= 0:
                print("[ENV] Simulation finished")
                msg_queue.put("STOP")
                return

        time.sleep(1)

