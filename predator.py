import socket
import time

def predator_process(shared_state, lock, msg_queue):
    energy = 60

    # Connexion au socket pour s'enregistrer auprès de l'environnement
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1024))
        sock.close()
    except:
        return

    try:
        while energy > 0:
            energy -= 3 # Diminution régulière de l'énergie

            # Tentative de chasse si l'énergie est basse (seuil H = 40)
            if energy < 40:
                with lock:
                    # Vérification stricte : on ne mange que s'il y a des proies ACTIVES
                    # Cela empêche le nombre de proies de devenir négatif
                    if shared_state["num_active_preys"] > 0:
                        shared_state["num_preys"] -= 1
                        shared_state["num_active_preys"] -= 1
                        energy += 70
                        msg_queue.put("PRÉDATION !")
            
            # Reproduction si l'énergie est élevée (seuil R = 80)
            if energy > 80:
                energy -= 50
                msg_queue.put("Naissance prédateur")

            time.sleep(1)

    finally:
        with lock:
            shared_state["num_predators"] -= 1
        msg_queue.put("Un prédateur est mort")
