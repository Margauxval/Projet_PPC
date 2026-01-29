#!/usr/bin/env python3

import socket, time, signal, os

def env_process(shared_state, msg_queue, lock):
    start_time = time.time()
    ready = False
    drought_timer = 0
    with lock: shared_state["drought_active"] = False

    # Handler de signal : exécuté quand on reçoit SIGUSR1 
    def handle_sigusr1(s, f):
        nonlocal drought_timer #permet modification de variable définie à l'extérieur
        with lock: shared_state["drought_active"] = True
        drought_timer = 8 # Durée de la sécheresse en secondes
        msg_queue.put("DÉBUT SÉCHERESSE")

    signal.signal(signal.SIGUSR1, handle_sigusr1) # si signal reçu pas d'arrêt et exécution fonction
    
    # Création d'un socket pour synchroniser le démarrage des agents
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Af_INET = IP ; SOCK_STREAM = TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # relancer code rapidement sans port occupé 
    server.bind(("localhost", 1024))
    server.listen(128)
    server.setblocking(False)

    last_tick = time.time()
    try:
        while True:
            with lock:
                cp, cd, cg = shared_state["num_preys"], shared_state["num_predators"], shared_state["grass"]
            
            # Détermine si la simulation a vraiment commencé
            if not ready and (cp > 0 or time.time() - start_time > 5): ready = True
            
            # Condition de fin : si une espèce disparaît
            if ready and (cp <= 0 or cd <= 0):
                msg_queue.put(("BILAN", f"Fin | Proies: {cp} | Preds: {cd} | Herbe: {cg}"))
                return

            # Lecture des commandes envoyées par l'affichage (Pygame)
            while not msg_queue.empty():
                try:
                    m = msg_queue.get_nowait() # si pas de message dans queue pas d'attente et lancement erreur
                    if m == ("CMD", "STOP"):
                        msg_queue.put(("BILAN", f"Manuel | Proies: {cp} | Preds: {cd} | Herbe: {cg}")); return
                    if m == ("CMD", "FORCED_DROUGHT"):
                        # S'envoie un signal à soi-même pour déclencher handle_sigusr1
                        os.kill(os.getpid(), signal.SIGUSR1)
                except: break

            # Mise à jour de l'herbe toutes les secondes
            if time.time() - last_tick > 1.0:
                last_tick = time.time()
                with lock:
                    if not shared_state["drought_active"]: 
                        shared_state["grass"] += 35 
                    else:
                        drought_timer -= 1
                        if drought_timer <= 0: 
                            shared_state["drought_active"] = False # Fin de sécheresse
            
            # Accepte les connexions "vides" des agents (juste pour leur dire "je suis prêt")
            try:
                c, _ = server.accept(); c.close()
            except: pass
            time.sleep(0.1)
    finally: server.close()
