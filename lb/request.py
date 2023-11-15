from uuid import uuid4


class Request:
    def __init__(self, results_queue, fn, *args):
        self.fn = fn
        self.args = args
        self.results_queue = results_queue
        self.id = uuid4()

    def __repr__(self):
        return str(self.id)[-6:]

    def evaluate_and_return_result(self):
        self.result = self.fn(*self.args)
        self.results_queue.put(self)
