from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process
import time
import os
import signal

if __name__ == "__main__":
    # --- Configuration interactive (tes paramètres) ---
    print("=== Configuration de la Simulation ===")
    g_init = int(input("Quantité d'herbe initiale (def: 30) : ") or 30)
    prey_init = int(input("Nombre de proies initial (def: 5) : ") or 5)
    pred_init = int(input("Nombre de prédateurs initial (def: 2) : ") or 2)
    drought_time = int(input("Déclenchement sécheresse automatique (secondes, 0=jamais) : ") or 10)

    manager = Manager()
    lock = Lock()
    msg_queue = Queue()

    # État partagé synchronisé
    shared_state = manager.dict({
        "grass": g_init,
        "num_preys": prey_init,
        "num_active_preys": 0,
        "num_predators": pred_init
    })

    # Définition des processus
    display = Process(target=display_process, args=(msg_queue,))
    env = Process(target=env_process, args=(shared_state, msg_queue, lock))
    prey = Process(target=prey_process, args=(shared_state, lock, msg_queue))
    predator = Process(target=predator_process, args=(shared_state, lock, msg_queue))

    # Lancement ordonné
    display.start()
    env.start()
    
    # Très important : on attend que l'ENV ait bind le port 1024 
    # avant que les agents essaient de s'y connecter
    time.sleep(1.5) 
    
    prey.start()
    predator.start()

    # Gestion du signal de sécheresse automatique si activé
    if drought_time > 0:
        time.sleep(drought_time)
        if env.is_alive():
            msg_queue.put("MAIN : Envoi du signal SIGUSR1 (Sécheresse)")
            os.kill(env.pid, signal.SIGUSR1)

    # Attente de la fin de la simulation
    env.join()
    prey.join()
    predator.join()
    display.join()

    print("\n[MAIN] Simulation terminée proprement.")
