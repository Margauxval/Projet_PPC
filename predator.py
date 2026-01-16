import socket
import time
import random

ACTIVE = "ACTIVE"
PASSIVE = "PASSIVE"

def predator_process(shared_state, lock):
    energy = 50
    state = PASSIVE

    # Join env
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))
    sock.close()

    while energy >= 0:
        energy -= 1

        if energy < 30:
            state = ACTIVE
        elif energy > 60:
            state = PASSIVE

        if state == ACTIVE:
            with lock:
                if shared_state["num_preys"] > 0:
                    shared_state["num_preys"] -= 1
                    energy += 20

        time.sleep(1)

    print("Predator died")
