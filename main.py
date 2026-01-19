from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
import time

def display_process(msg_queue):
    while True:
        if not msg_queue.empty():
            msg = msg_queue.get()
            if msg == "STOP":
                break
            print(f"[DISPLAY] {msg}")
        time.sleep(0.5)  # pour ne pas spammer le terminal

if __name__ == "__main__":
    manager = Manager()
    lock = Lock()

    # état partagé
    shared_state = manager.dict({
        "grass": 30,
        "num_preys": 1,
        "num_predators": 3
    })

    msg_queue = Queue()

    # lancer les processus
    env = Process(target=env_process, args=(shared_state, msg_queue, lock))
    prey = Process(target=prey_process, args=(shared_state, lock))
    predator = Process(target=predator_process, args=(shared_state, lock))
    display = Process(target=display_process, args=(msg_queue,))

    print("[MAIN] Starting env process")
    env.start()
    time.sleep(0.5)  # laisser le temps au serveur de démarrer

    print("[MAIN] Starting predator and prey")
    prey.start()
    predator.start()
    display.start()

    # attendre la fin
    env.join()
    prey.join()
    predator.join()
    display.join()

    print("[MAIN] Simulation ended")
