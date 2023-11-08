_worker_id = -1
_requester_id = -1
_request_id = -1
_work_id = -1


def work_id():
    global _work_id
    _work_id += 1
    return _work_id


def worker_id():
    global _worker_id
    _worker_id += 1
    return _worker_id


def requester_id():
    global _requester_id
    _requester_id += 1
    return _requester_id


def request_id():
    global _request_id
    _request_id += 1
    return _request_id
