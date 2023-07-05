from typing import Callable, List, Any

class Batcher:
    processed_count: int
    def __init__(self, batch_size: int, flush_handler: Callable[[List[Any]], None]):
        self.batch_size = batch_size
        self.buffer = []
        self.flush_handler = flush_handler
        self.processed_count = 0

    def add(self, item: Any):
        self.processed_count += 1
        self.buffer.append(item)
        self.flush_if_necessary()

    def flush(self):
        if len(self.buffer) == 0:
            return
        self.flush_handler(self.buffer)
        self.buffer.clear()

    def flush_if_necessary(self):
        if len(self.buffer) >= self.batch_size:
            self.flush()
