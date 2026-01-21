import sys
import time
import select

def display_process(msg_queue):
    print("""
=== DISPLAY CONTROLS ===
p : pause
r : resume
d : drought
q : quit
========================
""")

    while True:
        # 1️⃣ affichage états
        while not msg_queue.empty():
            msg = msg_queue.get()
            if msg == "STOP":
                print("[DISPLAY] Simulation ended")
                return
            print(f"[DISPLAY] {msg}")

        # 2️⃣ lecture clavier NON BLOQUANTE
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)

            if key == "p":
                msg_queue.put(("CMD", "PAUSE"))
                print("[DISPLAY] pause")

            elif key == "r":
                msg_queue.put(("CMD", "RESUME"))
                print("[DISPLAY] resume")

            elif key == "d":
                msg_queue.put(("CMD", "DROUGHT"))
                print("[DISPLAY] drought")

            elif key == "q":
                msg_queue.put(("CMD", "STOP"))
                print("[DISPLAY] quit")
                return

        time.sleep(0.1)
