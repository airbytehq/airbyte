#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import cProfile
import io
import pstats
import time
from pstats import SortKey

from source_s3.run import run

if __name__ == "__main__":

    profiler = cProfile.Profile()
    profiler.enable()

    current_time = time.time()

    run()

    end_time = time.time()

    print("-------------------END OUTPUT-------------------")

    profiler.disable()
    profiler_output = io.StringIO()
    pstats.Stats(profiler, stream=profiler_output).sort_stats(SortKey.TIME).print_stats(25)
    print(profiler_output.getvalue())

    print(f"Time taken: {end_time - current_time}")
