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

    pr = cProfile.Profile()
    pr.enable()


    current_time = time.time()

    run()

    end_time = time.time()

    pr.disable()
    s = io.StringIO()
    sortby = SortKey.TIME
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(25)
    print(s.getvalue())

    print(f"Time taken: {end_time - current_time}")
