from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process
import time

def spawn_prey(shared_state, lock, msg_queue):
    p = Process(target=prey_process, args=(shared_state, lock, msg_queue))
    p.start()
    return p

def spawn_pred(shared_state, lock, msg_queue):
    p = Process(target=predator_process, args=(shared_state, lock, msg_queue))
    p.start()
    return p

def safe_input(prompt, default):
    try:
        val = input(f"{prompt} (def: {default}) : ")
        if not val: return default
        # Nettoyage des caractères non numériques si besoin
        return int(''.join(filter(str.isdigit, val)))
    except:
        return default

if __name__ == "__main__":
    print("=== Configuration de la Simulation ===")
    g_init = safe_input("Herbe initiale", 100)
    p_init = safe_input("Nombre de proies", 12)
    d_init = safe_input("Nombre de prédateurs", 4)
    d_freq = safe_input("Fréquence sécheresse (cycles)", 20)

    manager = Manager()
    lock = Lock()
    msg_queue = Queue()

    # Initialisation de l'état partagé
    shared_state = manager.dict({
        "grass": g_init,
        "num_preys": p_init,          
        "num_active_preys": 0,
        "num_predators": d_init
    })

    p_display = Process(target=display_process, args=(msg_queue,))
    p_env = Process(target=env_process, args=(shared_state, msg_queue, lock, d_freq))
    
    p_display.start()
    p_env.start()
    time.sleep(1.5) # Temps d'attente pour le Socket de env.py

    all_agents = []
    # Lancement des processus agents
    for _ in range(p_init): 
        all_agents.append(spawn_prey(shared_state, lock, msg_queue))
    for _ in range(d_init): 
        all_agents.append(spawn_pred(shared_state, lock, msg_queue))

    try:
        while p_env.is_alive():
            if not msg_queue.empty():
                msg = msg_queue.get()
                if msg == "Naissance proie":
                    with lock: shared_state["num_preys"] += 1
                    all_agents.append(spawn_prey(shared_state, lock, msg_queue))
                elif msg == "Naissance prédateur":
                    with lock: shared_state["num_predators"] += 1
                    all_agents.append(spawn_pred(shared_state, lock, msg_queue))
                else:
                    msg_queue.put(msg)
            time.sleep(0.1)
    finally:
        for p in all_agents: 
            if p.is_alive(): p.terminate()
        p_env.terminate()
        p_display.join()
