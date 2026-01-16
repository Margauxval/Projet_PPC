import socket
import time

ACTIVE = "ACTIVE"
PASSIVE = "PASSIVE"

def prey_process(shared_state, lock):
    energy = 40
    state = PASSIVE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))
    sock.close()

    while energy >= 0:
        energy -= 1

        if energy < 20:
            state = ACTIVE
        elif energy > 50:
            state = PASSIVE

        if state == ACTIVE:
            with lock:
                if shared_state["grass"] > 0:
                    shared_state["grass"] -= 1
                    energy += 10

        time.sleep(1)

    print("Prey died")
