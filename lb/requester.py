import time
from multiprocessing import Manager

from lb.request import Request
import lb.ids


def workFn() -> int:
    time.sleep(0.01)  # do work
    return 1


def requester(work, requester: int):
    work_sent = 0
    work_done = 0

    c = Manager().Queue()
    for i in range(100):
        # while True:
        time.sleep(0.002)  # do work
        r = Request(workFn, c, requester, lb.ids.request_id())
        print(f"PUT,{r}")
        work.put(r)
        work_sent += 1
        # print(f"BLOCKING Waiting {r}")
        # This shouldnt block, should wait timeout then drain if not empty
        while not c.empty():
            result: Request = c.get()
            work_done += 1
            print(f"WRK,{result}")

    while work_done < work_sent:
        result: Request = c.get()
        work_done += 1
        print(f"FWR,{result}")
