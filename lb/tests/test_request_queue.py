from lb.request_queue import get_request_queue


def test_queue_type():
    request_queue = get_request_queue()
    assert request_queue.empty() == False
