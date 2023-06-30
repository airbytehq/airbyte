from typing import Callable, List, Any

class Batcher:
    def __init__(self, batch_size: int, flush_handler: Callable[[List[Any]], None]):
        self.batch_size = batch_size
        self.buffer = []
        self.flush_handler = flush_handler

    def add(self, item: Any):
        self.buffer.append(item)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        if self.buffer:
            # Process the batch
            self.flush_handler(self.buffer)
            self.buffer.clear()

    def flush_if_necessary(self):
        if len(self.buffer) >= self.batch_size:
            self.flush()
