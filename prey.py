import socket
import time
import errno

def prey_process(shared_state, lock, msg_queue):
    energy, was_active = 40, False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            sock.connect(("localhost", 1024))
            sock.setblocking(False)
            break
        except: time.sleep(0.5)

    try:
        while energy > 0:
            try:
                if sock.recv(1024) == b"END": break
            except socket.error: pass

            is_active = energy < 10
            if is_active != was_active:
                with lock:
                    shared_state["num_active_preys"] += 1 if is_active else -1
                was_active = is_active

            energy -= 1
            if is_active:
                with lock:
                    if shared_state["grass"] > 0:
                        shared_state["grass"] -= 1
                        energy += 30
            elif energy > 50:
                with lock:
                    shared_state["num_preys"] += 1
                    energy -= 15
                    msg_queue.put("Naissance proie")
            time.sleep(0.5)
    finally:
        with lock:
            shared_state["num_preys"] -= 1
            if was_active: shared_state["num_active_preys"] -= 1
        sock.close()
