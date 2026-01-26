from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process
import time

def spawn_prey(shared_state, lock, msg_queue, spawn_queue):
    p = Process(target=prey_process, args=(shared_state, lock, msg_queue, spawn_queue))
    p.start()
    return p

def spawn_pred(shared_state, lock, msg_queue, spawn_queue):
    p = Process(target=predator_process, args=(shared_state, lock, msg_queue, spawn_queue))
    p.start()
    return p

def safe_input(prompt, default):
    try:
        val = input(f"{prompt} (defaut: {default}) : ")
        if not val: return default
        return int(''.join(filter(str.isdigit, val)))
    except: return default

if __name__ == "__main__":
    g_init = safe_input("Herbe initiale", 200)
    p_init = safe_input("Nombre de proies", 50)
    d_init = safe_input("Nombre de prédateurs", 1)
    d_freq = safe_input("Durée de la sécheresse", 20)

    manager = Manager()
    lock = Lock()
    msg_queue = Queue()
    spawn_queue = Queue() 

    shared_state = manager.dict({
        "grass": g_init,
        "num_preys": p_init,          
        "num_active_preys": 0,
        "num_predators": d_init
    })

    p_display = Process(target=display_process, args=(shared_state, msg_queue, lock))
    p_env = Process(target=env_process, args=(shared_state, msg_queue, lock, d_freq))
    
    p_display.start()
    p_env.start()
    time.sleep(1.0)

    all_agents = []
    for _ in range(p_init): 
        all_agents.append(spawn_prey(shared_state, lock, msg_queue, spawn_queue))
    for _ in range(d_init): 
        all_agents.append(spawn_pred(shared_state, lock, msg_queue, spawn_queue))

    try:
        while p_env.is_alive():
            while not spawn_queue.empty():
                try:
                    type_birth = spawn_queue.get_nowait()
                    if type_birth == "PROIE":
                        with lock: shared_state["num_preys"] += 1
                        all_agents.append(spawn_prey(shared_state, lock, msg_queue, spawn_queue))
                    elif type_birth == "PRED":
                        with lock: shared_state["num_predators"] += 1
                        all_agents.append(spawn_pred(shared_state, lock, msg_queue, spawn_queue))
                except: break
            time.sleep(0.1)
    finally:
        for p in all_agents: 
            if p.is_alive(): p.terminate()
        p_env.terminate()
        p_display.join()
