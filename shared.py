from multiprocessing import Manager, Lock

def create_shared_state():
    manager = Manager()
    state = manager.dict({
        "grass": 100,
        "num_predators": 0,
        "num_preys": 0,
        "drought": False
    })
    lock = manager.Lock()
    return state, lock
