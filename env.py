import socket, time, signal, os

def env_process(shared_state, msg_queue, lock, drought_freq):
    start_time = time.time()
    ready = False
    drought_timer = 0
    cycle_count = 0 # Ajout d'un compteur de cycles
    with lock: shared_state["drought_active"] = False

    def handle_sigusr1(s, f):
        nonlocal drought_timer, cycle_count
        with lock: shared_state["drought_active"] = True
        drought_timer = 8 
        cycle_count = 0 # Réinitialise pour le prochain cycle
        msg_queue.put("DÉBUT SÉCHERESSE")

    signal.signal(signal.SIGUSR1, handle_sigusr1)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 1024))
    server.listen(128)
    server.setblocking(False)

    last_tick = time.time()
    try:
        while True:
            with lock:
                cp, cd, cg = shared_state["num_preys"], shared_state["num_predators"], shared_state["grass"]
            
            if not ready and (cp > 0 or time.time() - start_time > 5): ready = True
            
            if ready and (cp <= 0 or cd <= 0):
                msg_queue.put(("BILAN", f"Fin | Proies: {cp} | Preds: {cd} | Herbe: {cg}"))
                return

            while not msg_queue.empty():
                try:
                    m = msg_queue.get_nowait()
                    if m == ("CMD", "STOP"):
                        msg_queue.put(("BILAN", f"Manuel | Proies: {cp} | Preds: {cd} | Herbe: {cg}")); return
                    if m == ("CMD", "FORCED_DROUGHT"):
                        os.kill(os.getpid(), signal.SIGUSR1)
                except: break

            # Dans env_process
            if time.time() - last_tick > 1.0:
                last_tick = time.time()
                cycle_count += 1
                with lock:
                    if not shared_state["drought_active"]: 
                        shared_state["grass"] += 35 # Repousse augmentée pour nourrir le troupeau
                        if cycle_count >= drought_freq:
                            os.kill(os.getpid(), signal.SIGUSR1)
                    else:
                        drought_timer -= 1
                        if drought_timer <= 0: 
                            shared_state["drought_active"] = False
                            cycle_count = 0 # Reset crucial pour la boucle auto
            try:
                c, _ = server.accept(); c.close()
            except: pass
            time.sleep(0.1)
    finally: server.close()
