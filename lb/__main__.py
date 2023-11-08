from multiprocessing import Process, Manager

from lb.requester import requester
from lb.balancer import Balancer
import lb.ids


nRequester = 100
nWorker = 10

if __name__ == "__main__xxx":
    work = Manager().Queue()

    Balancer(nWorker).balance(work)

    procs = []
    for i in range(nRequester):
        p = Process(
            target=requester,
            args=(
                work,
                lb.ids.requester_id(),
            ),
        )
        p.start()
        procs.append(p)

    for p in procs:
        p.join()




if __name__ == "__main__":
    pass
