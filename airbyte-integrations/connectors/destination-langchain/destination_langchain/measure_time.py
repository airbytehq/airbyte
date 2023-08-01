#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        wrapper.total_time += execution_time
        wrapper.average_time = wrapper.total_time / wrapper.count

        return result

    wrapper.count = 0
    wrapper.total_time = 0
    wrapper.average_time = 0
    wrapper._get_stats = lambda: get_stats(wrapper)

    def get_stats(wrapper):
        return f"Function '{func.__name__}' called {wrapper.count} time(s).\nAverage execution time: {wrapper.average_time:.6f} seconds.\nTotal execution time: {wrapper.total_time:.6f} seconds."

    return wrapper
