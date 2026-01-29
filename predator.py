#!/usr/bin/env python3

import socket
import time

def predator_process(shared_state, lock, msg_queue, spawn_queue):
    energy = 100
    was_active = False 

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", 1024))
        sock.close()
    except:
        return 

    try:
        while energy > 0:
            is_active = energy < 120 
            
            if is_active != was_active:
                with lock:
                    current_active = shared_state.get("num_active_predators", 0)
                    if is_active:
                        shared_state["num_active_predators"] = current_active + 1
                    else:
                        shared_state["num_active_predators"] = max(0, current_active - 1)
                was_active = is_active

            energy -= 8 

            if is_active: 
                with lock:
                    if shared_state.get("num_active_preys", 0) > 0:
                        shared_state["num_preys"] = max(0, shared_state["num_preys"] - 1)
                        shared_state["num_active_preys"] = max(0, shared_state["num_active_preys"] - 1)
                        energy += 80 
                        msg_queue.put("PRÉDATION !")
            
            if energy > 160: 
                energy -= 80
                msg_queue.put("Naissance prédateur")
                spawn_queue.put("PRED")

            time.sleep(0.8)
    finally:
        with lock:
            shared_state["num_predators"] = max(0, shared_state["num_predators"] - 1)
            if was_active:
                current_active = shared_state.get("num_active_predators", 0)
                shared_state["num_active_predators"] = max(0, current_active - 1)
        
        msg_queue.put("Un prédateur est mort de faim")
