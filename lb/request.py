from uuid import uuid4


class Request:
    """request class to transport work function and parameters from the requester
    to the Worker via the Balancer and report result back to Requester
    """

    def __init__(self, results_queue, fn, *args):
        # The Callable to be executed
        self.fn = fn
        #  args to be passed to the Callable
        self.args = args
        # The queue along which to send the results
        self.results_queue = results_queue
        # unique id for the request
        self.id = uuid4()

    def __repr__(self):
        return str(self.id)[-6:]

    def evaluate_and_return_result(self):
        """Evaluate the function in the request and put the result onto the requesters
        results return queue for onward processing in the Requester process
        """
        self.result = self.fn(*self.args)
        self.results_queue.put(self)
