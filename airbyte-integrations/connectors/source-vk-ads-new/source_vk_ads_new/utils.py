from typing import Any, Iterable, Iterator, List


def chunks(lst: Iterable, n: int) -> Iterator[List[Any]]:
    """Yield successive n-sized chunks from lst."""
    if n < 1:
        raise ValueError("n argument must be more than 1")
    buffer = []
    for i in lst:
        if len(buffer) == n:
            yield buffer
            buffer = []
        buffer.append(i)
    if buffer:
        yield buffer
