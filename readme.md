concurrent
library independent
architecture relies only on ability to spawn and to communicate between processed
try to not use language specific process management to make translation/implementation straightforward
"work" is stateless, firstclass, idempotent function
passed state
example of generic work
conect to websockets to simulate "live" work

## Load balancer

1. start with run main
2. FIFO work request channel (could be parallelised if work order not important)
3. Pool of workers and ability to balance to least loaded worker (using a priority queue)
4. Worker communicate task completion back
5. Task status nWaiting/Scheduled/Complete
6. return queue to communicate task complete

Enhancements
Re-start un completed tasks
Use message broker e.g. ZMQ to handle inter-process comms
throttling/exponential backoff
add/remove workers dynamically via request queue
