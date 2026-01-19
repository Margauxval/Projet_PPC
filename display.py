import time
from multiprocessing import Queue

def display_process(msg_queue):
    while True:
        if not msg_queue.empty():
            state = msg_queue.get()
            if state == "STOP":
                print("[DISPLAY] Simulation ended")
                break
            print(f"[DISPLAY] {state}")
        time.sleep(0.5)
