import socket
import time
from multiprocessing import Manager, Lock, Queue

HOST = "localhost"
PORT = 1024

def env_process(shared_state, msg_queue, lock):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[ENV] Waiting for clients...")

    clients = []
    while len(clients) < 2:  # attendre 2 clients: prey + predator
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
                if shared_state["num_preys"] == 0 or shared_state["num_predators"] == 0:
                    print("[ENV] No preys or predators left. Ending simulation.")
                    
                    # Prévenir les clients
                    for client in clients:
                        try:
                            client.sendall(b"END")
                        except Exception:
                            pass  # le client peut déjà être fermé

                    # Stopper l'affichage et fermer le serveur
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
        msg_queue.put("STOP")

