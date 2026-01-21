from multiprocessing import Process, Manager, Lock, Queue
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process
import time

if __name__ == "__main__":

    print("=== Simulation parameters ===")
    grass = int(input("Initial grass amount: "))
    preys = int(input("Initial number of preys: "))
    predators = int(input("Initial number of predators: "))
    drought = int(input("Drought period (seconds, 0 = no drought): "))

    manager = Manager()
    lock = Lock()

    shared_state = manager.dict({
        "grass": grass,
        "num_preys": preys,
        "num_predators": predators,
        "drought": False,
        "drought_period": drought
    })

    msg_queue = Queue()

    env = Process(target=env_process, args=(shared_state, msg_queue, lock))
    prey = Process(target=prey_process, args=(shared_state, lock))
    predator = Process(target=predator_process, args=(shared_state, lock))
    display = Process(target=display_process, args=(msg_queue,))

    print("[MAIN] Starting env process")
    env.start()
    time.sleep(0.5)

    print("[MAIN] Starting predator, prey and display")
    prey.start()
    predator.start()
    display.start()

    env.join()
    prey.join()
    predator.join()
    display.join()

    print("[MAIN] Simulation ended")
