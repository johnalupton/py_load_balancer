from uuid import uuid4

from lb.constants import STOP
from lb.request import Request


def work_fn(*args):
    """Dummy work function to simulate load on CPU

    Returns:
        Any: As a default return value returns the first argument passed
    """
    for i in range(100000000):
        pass
    return args[0]


class Requester:
    """Utility class to generate work to send to the balancer"""

    def __init__(self, requests_queue, manager):
        # The request queue of the balancer receiving the Requests
        self.requests_queue = requests_queue
        # The queue along which this Requester wants to receive resukts of work direct from the Worker
        self.results_queue = manager.Queue()
        # Audit of results received back
        self.results_received = 0
        # Requester id
        self.id = uuid4()

    def __repr__(self):
        """User friendly uuid

        Returns:
            str: last 6 chars of the uuid for ease of identification
        """
        return str(self.id)[-6:]

    def generate_requests(self, num_requests: int):
        """Generate dummy work.

        Args:
            num_requests (int): number of requests to generate
        """
        for i in range(num_requests):
            # set up a new Request with the dummy work_fn and arbitrary parameter i
            req = Request(self.results_queue, work_fn, i)
            # put the new request onto the balancers requests queue
            self.requests_queue.put(req)

    def stop_polling_results(self):
        """Send a STOP message to the results queue for this Requester to stop the
        poll_results process
        """
        self.results_queue.put(STOP)

    def poll_results(self):
        """Report any results that are on the resukts queue for this Requester process"""
        loop_for_results = True
        while loop_for_results:
            while not self.results_queue.empty():
                # pull the now-complete request off the results queue
                req: Request = self.results_queue.get()

                # if the request is STOP then break the loop
                if req == STOP:
                    loop_for_results = False
                else:
                    # log to stdout a valid result
                    self.results_received += 1
                    print(f"Requester {self} result {req} = {req.result}>")

        # log to stdout summary results for this Requester
        print(
            f"Requester {self} stop polling with {self.results_received} received results"
        )
