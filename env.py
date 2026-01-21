import socket
import time
import signal

# Variable globale pour l'état de la sécheresse
drought_active = False

def handle_drought(signum, frame):
    """Handler déclenché par le signal SIGUSR1 envoyé par le main"""
    global drought_active
    drought_active = not drought_active

def env_process(shared_state, msg_queue, lock):
    global drought_active
    
    # 1. Configuration du Signal SIGUSR1
    signal.signal(signal.SIGUSR1, handle_drought)
    
    # 2. Configuration du Serveur Socket (TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR permet de relancer le script immédiatement sans attendre l'OS
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(("localhost", 1024))
    except OSError as e:
        msg_queue.put(f"ERREUR ENV : Port 1024 occupé. ({e})")
        return

    server.listen()
    msg_queue.put("ENV : Serveur prêt, en attente des agents (Prey/Predator)...")

    clients = []
    # On attend la connexion des deux agents (un processus prey et un predator)
    while len(clients) < 2:
        client, _ = server.accept()
        clients.append(client)
    
    msg_queue.put("ENV : Connexions établies. Lancement de la simulation.")

    cycle_count = 0
    
    try:
        while True:
            # --- A. Gestion des commandes venant du Display (ex: touche 'q') ---
            while not msg_queue.empty():
                cmd = msg_queue.get()
                if cmd == ("CMD", "STOP"):
                    msg_queue.put("ENV : Arrêt demandé par l'utilisateur.")
                    return 

            # --- B. Cycle automatique de Sécheresse (toutes les 10 secondes) ---
            cycle_count += 1
            if cycle_count >= 10:
                drought_active = not drought_active
                cycle_count = 0
                msg_queue.put(f"ENV : Sécheresse {'DÉBUT' if drought_active else 'FIN'}")

            # --- C. Mise à jour de la Simulation ---
            with lock:
                # L'herbe ne pousse que s'il n'y a pas de sécheresse
                if not drought_active:
                    shared_state["grass"] += 2
                
                # Formatage du statut pour l'affichage (Dashboard)
                status = (f"Herbe: {shared_state['grass']} | "
                          f"Proies: {shared_state['num_preys']} (Actives: {shared_state['num_active_preys']}) | "
                          f"Preds: {shared_state['num_predators']}")
                
                if drought_active:
                    status += " [SÉCHERESSE]"
                
                msg_queue.put(status)

                # --- D. Condition de fin automatique ---
                if shared_state["num_preys"] <= 0 or shared_state["num_predators"] <= 0:
                    msg_queue.put("ENV : Une population a disparu. Fin.")
                    break
            
            time.sleep(1) # Un cycle par seconde

    finally:
        # --- E. Nettoyage et Fermeture ---
        # On prévient les agents via le socket avant de fermer
        for c in clients:
            try:
                c.sendall(b"END")
                c.close()
            except:
                pass
        server.close()
        time.sleep(0.2) # Laisser le temps aux messages de partir
        msg_queue.put("STOP") # Indique au Display de s'éteindre
