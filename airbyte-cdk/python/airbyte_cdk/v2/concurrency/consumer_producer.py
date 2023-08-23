import concurrent.futures
import time
import queue
import random

shared_queue = queue.Queue()

_SENTINEL = "SENTINEL"

def producer(id):
    number_of_partitions = random.randint(1, 5)
    sleep = id % 2 == 0
    if sleep:
        print(f"Producer {id} sleeping for 1 second")
        # The sleep simulates potentially submitting requests to the parent stream
        # The response might already be in the cache
        time.sleep(1)
    for i in range(number_of_partitions):
        print(f"Producer {id} produced {i}")
        shared_queue.put({"stream": id, "partition": i})
    return

def consumer(id):
    while True:
        try:
            item = shared_queue.get(timeout=2)
            if item == _SENTINEL:
                print(f"found sentinel, exiting")
                break
            print(f"Consumer {id} consumed {item}")
            # This sleep simulates submitting a request to the API and generating records from it
            time.sleep(1)
            shared_queue.task_done()
        except queue.Empty:
            print(f"Consumer {id} timed out waiting for an item.")

if __name__ == "__main__":
    num_producers = 2
    num_consumers = 3
    items_to_produce = [i for i in range(10)]
    producer_futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_producers + num_consumers) as executor:
        # First, generate the partitions in parallel
        for i in items_to_produce:
            producer_future = executor.submit(producer, i)
            producer_futures.append(producer_future)

        # Then, consume the partitions in parallel
        # The partitions might not all be done, but that's ok. some of them will be slow
        for i in range(num_consumers):
            executor.submit(consumer, i)

        print(f"done submitting tasks")
        concurrent.futures.wait(producer_futures)
        print(f"done generating partitions")
        # Add sentinel values to the queue to signal the consumers to exit
        # Add one per consumer so they all exit
        for _ in range(num_consumers):
            shared_queue.put(_SENTINEL)
