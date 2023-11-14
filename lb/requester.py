from multiprocessing import Queue
from time import sleep


def work():
    import random

    w = random.uniform(0, 1)
    print(f"working for {w}", flush=True)
    sleep(w)


def make_requests(requester_control_queue: Queue, id):
    keep_requesting = True

    while keep_requesting:
        # sleep(0.1)
        print(f"{id} Requesting", flush=True)

        while not requester_control_queue.empty():
            message = requester_control_queue.get()
            if message is None:
                keep_requesting = False
                break
