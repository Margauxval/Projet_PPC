import socket
import time

def predator_process(shared_state, lock, msg_queue, spawn_queue):
    energy = 100
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1024))
        sock.close()
    except: return

    try:
        while energy > 0:
            energy -= 8 # Perte lente pour lui donner une chance de trouver une proie

            # Le prédateur chasse dès qu'il n'est pas "plein"
            if energy < 120: 
                with lock:
                    if shared_state["num_active_preys"] > 0:
                        shared_state["num_preys"] = max(0, shared_state["num_preys"] - 1)
                        shared_state["num_active_preys"] = max(0, shared_state["num_active_preys"] - 1)
                        energy += 80 # Gros gain pour récompenser la chasse
                        msg_queue.put("PRÉDATION !")
            
            if energy > 160: # Se reproduit uniquement s'il a bien mangé
                energy -= 80
                msg_queue.put("Naissance prédateur")
                spawn_queue.put("PRED")

            time.sleep(0.8)
    finally:
        # Si on sort de la boucle, c'est que energy <= 0
        with lock:
            shared_state["num_predators"] = max(0, shared_state["num_predators"] - 1)
        msg_queue.put("Un prédateur est mort de faim")
