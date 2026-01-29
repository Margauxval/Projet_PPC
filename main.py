#!/usr/bin/env python3

from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process
import time

# Fonction pour instancier une nouvelle proie dans un processus séparé
def spawn_prey(shared_state, lock, msg_queue, spawn_queue):
    p = Process(target=prey_process, args=(shared_state, lock, msg_queue, spawn_queue))
    p.start()
    return p

# Fonction pour instancier un nouveau prédateur dans un processus séparé
def spawn_pred(shared_state, lock, msg_queue, spawn_queue):
    p = Process(target=predator_process, args=(shared_state, lock, msg_queue, spawn_queue))
    p.start()
    return p

# Gère les demandes d'initialisation 
def safe_input(prompt, default):
    try:
        val = input(f"{prompt} (defaut: {default}) : ") #phrase demandée à l'utilisateur
        if not val: return default # si rien valeur par défaut  
        return int(''.join(filter(str.isdigit, val))) 
            #filter(str.isdigit, val)' : Parcourt la saisie et ne garde que les caractères numériques (0-9)
            #''.join(...) : Recolle ces chiffres ensemble pour reformer une chaîne de caractères propre
    except: return default # retourne vameur par défaut pour toute erreur 

if __name__ == "__main__":
    # Configuration initiale via la console
    g_init = safe_input("Herbe initiale", 600)
    p_init = safe_input("Nombre de proies", 200)
    d_init = safe_input("Nombre de prédateurs", 1)

    # Initialisation des outils de communication inter-processus
    manager = Manager()
    lock = Lock() 
    msg_queue = Queue() # Pour les logs et les commandes (Ex: Sécheresse)
    spawn_queue = Queue() # Pour signaler la naissance de nouveaux agents

    # Structure de données partagée entre TOUS les processus
    shared_state = manager.dict({
        "grass": g_init,
        "num_preys": p_init,          
        "num_active_preys": 0,
        "num_predators": d_init
    })

    # Lancement des processus de base (Affichage et Environnement)
    p_display = Process(target=display_process, args=(shared_state, msg_queue, lock))
    p_env = Process(target=env_process, args=(shared_state, msg_queue, lock))
    
    p_display.start()
    p_env.start()
    time.sleep(1.0) # Laisse le temps au serveur socket de démarrer dans env.py

    # Création de la population initiale
    all_agents = []
    for _ in range(p_init): 
        all_agents.append(spawn_prey(shared_state, lock, msg_queue, spawn_queue))
    for _ in range(d_init): 
        all_agents.append(spawn_pred(shared_state, lock, msg_queue, spawn_queue))

    try:
        # Boucle principale : surveille si la simulation doit continuer
        while p_env.is_alive():
            # Vérifie si un agent a demandé une naissance
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
        # Nettoyage final : on tue tous les processus pour libérer la RAM
        for p in all_agents: 
            if p.is_alive(): p.terminate()
        p_env.terminate()
        p_display.join()
