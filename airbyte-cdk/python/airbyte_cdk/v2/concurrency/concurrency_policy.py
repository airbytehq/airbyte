from abc import ABC, abstractmethod


class ConcurrencyPolicy(ABC):
    # Static
    # Can it also be dynamic? e.g: depending on what the server returns, change your params
    # TODO we need a 'thing' which decides if the sync is over e.g: if the daily rate limit was exceeded
    #  or if we've made more requests per minute than we want.
    #  it's sort of like a semaphore which could throw a RATE_LIMIT_EXHAUSTED exception with a timeout
    @abstractmethod
    def inspect_response(self):
        """ Gets the latest response"""
