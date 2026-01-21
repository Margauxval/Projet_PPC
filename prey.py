import socket
import time

def prey_process(shared_state, lock, msg_queue):
    energy = 50
    was_active = False

    # Connexion au socket de l'environnement pour "rejoindre" la simulation
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1024))
        sock.close()
    except:
        return # Arrêt si l'environnement n'est pas disponible

    try:
        while energy > 0:
            # État déterminé par l'énergie : active si énergie < 35 (H)
            is_active = energy < 35
            
            # Mise à jour du compteur d'individus actifs dans la mémoire partagée
            if is_active != was_active:
                with lock:
                    shared_state["num_active_preys"] += 1 if is_active else -1
                was_active = is_active

            energy -= 20 # Diminution régulière de l'énergie

            if is_active:
                with lock:
                    # Vérification stricte pour éviter que l'herbe devienne négative
                    if shared_state["grass"] > 0:
                        shared_state["grass"] -= 1
                        energy += 40
                        msg_queue.put("Une proie a mangé")
            
            # Reproduction si l'énergie dépasse le seuil R (80)
            elif energy > 70:
                energy -= 45
                msg_queue.put("Naissance proie")

            time.sleep(1)

    finally:
        # Nettoyage lors de la mort de la proie
        with lock:
            shared_state["num_preys"] -= 1
            if was_active:
                shared_state["num_active_preys"] -= 1
        msg_queue.put("Une proie est morte")
