from multiprocessing import Process, Queue
from shared import create_shared_state
from env import env_process
from predator import predator_process
from prey import prey_process
from display import display_process

if __name__ == "__main__":
    shared_state, lock = create_shared_state()
    msg_queue = Queue()

    env = Process(target=env_process, args=(shared_state, lock, msg_queue))
    disp = Process(target=display_process, args=(shared_state, msg_queue))
    pred = Process(target=predator_process, args=(shared_state, lock))
    prey = Process(target=prey_process, args=(shared_state, lock))

    env.start()
    disp.start()
    pred.start()
    prey.start()
