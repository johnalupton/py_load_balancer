from uuid import uuid4

from lb.constants import STOP
from lb.request import Request


class Worker:
    """Process to execute work defined in a Request
    """
    def __init__(self, manager):
        # the queue of Requests that have been allocated by the Balancer to this Worker
        self.worker_request_queue = manager.Queue()
        # counter of requests received - audit
        self.requests_received = 0
        # id of this worker - audit
        self.id = uuid4()

    def __repr__(self):
        return str(self.id)[-6:]

    def stop_working(self):
        """Send a STOP signal to this worker
        """
        self.worker_request_queue.put(STOP)

    def do_work(self, done_queue):
        """Loop to evaluate the work in a request, dispatch the results to the Requester
        and notify the Balancer

        Args:
            done_queue (multiprocessing.Queue): Queue along which to notify the Balancer that a request is done
        """
        loop_for_requests = True
        while loop_for_requests:
            while not self.worker_request_queue.empty():
                # get the next request from this Workers request queue
                req: Request = self.worker_request_queue.get()

                #  break the loop if STOP signalled
                if req == STOP:
                    loop_for_requests = False
                else:
                    # increment requests received
                    self.requests_received += 1
                    # evealuate the request and return the result to the Requester process
                    req.evaluate_and_return_result()
                    # Notify the Balancer that this request is done
                    done_queue.put((req.__repr__(), req.result))
