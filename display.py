import time

def display_process(shared_state, msg_queue):
    import time
    for _ in range(5):
        print("DISPLAY:", dict(shared_state))
        time.sleep(1)