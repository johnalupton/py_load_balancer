from uuid import uuid4

from lb.constants import STOP
from lb.request import Request


def work_fn(*args):
    for i in range(100000000):
        pass
    return args[0]


class Requester:
    def __init__(self, requests_queue, manager):
        self.requests_queue = requests_queue
        self.results_queue = manager.Queue()
        self.results_received = 0
        self.id = uuid4()

    def __repr__(self):
        return str(self.id)[-6:]

    def generate_requests(self, n: int):
        for i in range(n):
            req = Request(self.results_queue, work_fn, i)
            self.requests_queue.put(req)

    def stop_polling_results(self):
        self.results_queue.put(STOP)

    def poll_results(self):
        loop_for_results = True
        while loop_for_results:
            while not self.results_queue.empty():
                req: Request = self.results_queue.get()

                if req == STOP:
                    loop_for_results = False
                else:
                    self.results_received += 1
                    print(f"Requester {self} result {req} = {req.result}>")

        print(
            f"Requester {self} stop polling with {self.results_received} received results"
        )
