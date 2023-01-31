from typing import Mapping


from typing import List, Any


class ReportsCreator:
    max_concurrent_creating_reports_n = 5
    # TODO Make stream reports creation concurrent

    def __init__(self, stream_slices: List[Mapping[str, Any]]):
        self.stream_slices_queue = stream_slices
        self.current_creating_reports = []
