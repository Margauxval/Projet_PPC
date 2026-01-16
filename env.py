import signal
import socket
import time

def handle_drought(signum, frame, shared_state):
    print("Drought started!")
    shared_state["drought"] = True

def env_process(shared_state, lock, msg_queue):
    signal.signal(signal.SIGUSR1,lambda s, f: handle_drought(s, f, shared_state))

    # Socket to accept predators/preys
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5000))
    server.listen()

    while True:
        # Grass growth
        with lock:
            if not shared_state["drought"]:
                shared_state["grass"] += 1

        # Handle display messages
        if not msg_queue.empty():
            msg = msg_queue.get()
            if msg == "STOP":
                break

        time.sleep(1)