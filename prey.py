import socket
import time

def prey_process(shared_state, lock, msg_queue, spawn_queue):
    energy = 50
    was_active = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1024))
        sock.close()
    except: return 

    # Dans prey_process
   # Dans prey_process
    try:
        while energy > 0:
            # La proie devient active si son énergie tombe sous 80 (très vite)
            is_active = energy < 50 
            if is_active != was_active:
                with lock:
                    if is_active: shared_state["num_active_preys"] += 1
                    else: shared_state["num_active_preys"] = max(0, shared_state["num_active_preys"] - 1)
                was_active = is_active

            energy -= 8 # Consommation plus rapide pour forcer l'activité

            if is_active:
                with lock:
                    if shared_state["grass"] > 0:
                        shared_state["grass"] -= 1
                        energy += 30 # Gain modéré pour rester souvent en recherche
                        msg_queue.put("Une proie a mangé")
            
            elif energy > 60: # Seuil de reproduction plus difficile à atteindre
                energy -= 30
                msg_queue.put("Naissance proie")
                spawn_queue.put("PROIE")

            time.sleep(1.0)
    finally:
        with lock:
            shared_state["num_preys"] = max(0, shared_state["num_preys"] - 1)
            if was_active: shared_state["num_active_preys"] = max(0, shared_state["num_active_preys"] - 1)
        msg_queue.put("Une proie est morte de faim")
