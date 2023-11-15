from time import sleep

from lb.constants import STOP
from lb.request import Request


class Balancer:
    def __init__(self, manager):
        self.request_queue = manager.Queue()
        self.done_queue = manager.Queue()
        self.requests_received = 0
        self.workers = []
        self.last_worker = 0

    def next_worker(self):
        self.last_worker = (self.last_worker + 1) % len(self.workers)
        return self.workers[self.last_worker]

    def balance_requests(self):
        loop_for_requests = True
        while loop_for_requests:
            while not self.request_queue.empty():
                req: Request = self.request_queue.get()

                if req == STOP:
                    loop_for_requests = False
                    print(
                        f"Request polling stopped - {self.requests_received} requests received",
                        flush=True,
                    )
                else:
                    self.requests_received += 1
                    self.next_worker().worker_request_queue.put(req)

    def stop_requests(self):
        # stop sending requests to workers
        self.request_queue.put(STOP)

        # do nothing until request queue empty
        while not self.request_queue.empty():
            sleep(0.01)

        # send stop signal to workers
        for w in self.workers:
            w.stop_working()

    def drain_work_done(self):
        count = 0
        while not self.done_queue.empty():
            req_id, result = self.done_queue.get()
            print(f"Done request {req_id} with result {result}")
            count += 1
        print(f"{count} requests were done")
