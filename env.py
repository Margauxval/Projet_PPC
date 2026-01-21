import socket
import time
import signal
import os

def env_process(shared_state, msg_queue, lock, drought_freq):
    drought = {"active": False, "timer": 0}
    cycle_count = 0
    start_time = time.time()
    
    # Initialisation du statut pour éviter une erreur si le bilan est appelé tôt
    status = "Initialisation..."

    def handle_sigusr1(signum, frame):
        drought["active"] = True
        drought["timer"] = 6
        msg_queue.put("ALERTE : Sécheresse !")

    # Configuration du signal pour la sécheresse
    signal.signal(signal.SIGUSR1, handle_sigusr1)

    # Configuration du Socket (Consigne obligatoire)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 1024))
    server.listen(50)
    server.setblocking(False)

    last_tick = time.time()

    try:
        while True:
            # --- 1. Gestion des commandes (Queue) ---
            # On traite les messages, mais on ne traite qu'un certain nombre 
            # pour éviter une boucle infinie si on remet un message dans la file
            for _ in range(msg_queue.qsize()):
                try:
                    cmd = msg_queue.get_nowait()
                    if cmd == ("CMD", "STOP"):
                        return
                    elif cmd == ("CMD", "FORCED_DROUGHT"):
                        # Auto-envoi du signal SIGUSR1
                        os.kill(os.getpid(), signal.SIGUSR1)
                    else:
                        # Si ce n'est pas une commande pour l'env, on le remet 
                        # pour que le display puisse le lire (logs, etc.)
                        msg_queue.put(cmd)
                except:
                    break

            # --- 2. Mise à jour de l'environnement ---
            now = time.time()
            # Délai augmenté à 1.0 seconde pour une simulation plus longue
            if now - last_tick > 1.0: 
                last_tick = now
                cycle_count += 1

                # Déclenchement automatique de la sécheresse
                if cycle_count % drought_freq == 0 and not drought["active"]:
                    os.kill(os.getpid(), signal.SIGUSR1)

                with lock:
                    # Gestion de l'herbe
                    if drought["active"]:
                        drought["timer"] -= 1
                        if drought["timer"] <= 0:
                            drought["active"] = False
                    else:
                        shared_state["grass"] += 1

                    # Protection ABSOLUE contre les nombres négatifs (Clamping)
                    shared_state["grass"] = max(0, shared_state["grass"])
                    shared_state["num_preys"] = max(0, shared_state["num_preys"])
                    shared_state["num_predators"] = max(0, shared_state["num_predators"])
                    shared_state["num_active_preys"] = max(0, shared_state["num_active_preys"])

                    # Construction du message de statut pour le display
                    status = (
                        f"Herbe: {shared_state['grass']} | "
                        f"Proies: {shared_state['num_preys']} | "
                        f"Prédateurs: {shared_state['num_predators']}"
                    )
                    if drought["active"]:
                        status += " [SÉCHERESSE]"

                    msg_queue.put(status)

                    # Condition d'arrêt : on attend 20s au début pour laisser les populations s'installer
                    if time.time() - start_time > 20:
                        if shared_state["num_preys"] <= 0 or shared_state["num_predators"] <= 0:
                            break

            # --- 3. Acceptation des Sockets (non-bloquant) ---
            try:
                conn, _ = server.accept()
                conn.close()
            except (BlockingIOError, OSError):
                pass

            time.sleep(0.05) # Petite pause pour libérer le CPU

    finally:
        server.close()
        # Envoi du bilan final au processus d'affichage
        msg_queue.put(("BILAN", f"Simulation terminée | {status}"))
