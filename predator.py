import socket
import time

def predator_process(shared_state, lock, msg_queue):
    energy = 50
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            sock.connect(("localhost", 1024))
            sock.setblocking(False)
            break
        except: time.sleep(0.5)

    try:
        while energy > 0:
            try:
                if sock.recv(1024) == b"END": break
            except: pass

            energy -= 1
            if energy < 30:
                with lock:
                    if shared_state["num_active_preys"] > 0:
                        # On décrémente la population totale, 
                        # la proie gérera son compteur actif dans son finally
                        shared_state["num_preys"] -= 1
                        energy += 50
                        msg_queue.put("Prédation réussie !")
            time.sleep(0.5)
    finally:
        with lock: shared_state["num_predators"] -= 1
        sock.close()
