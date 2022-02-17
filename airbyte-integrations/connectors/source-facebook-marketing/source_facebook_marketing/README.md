## Structure

- api.py - everything related to FB API, error handling, throttle, call rate
- source.py - mainly check and discovery logic
- spec.py - connector's specification
- streams/ - everything related to streams, usually it is a module, but we have too much for one file
  - base_streams.py - all general logic should go there, you define class of streams as general as possible
  - streams.py - concrete classes, one for each stream, here should be only declarative logic and small overrides
  - base_insights_streams.py - piece of general logic for big subclass of streams - insight streams

  - async_job.py - logic about asynchronous jobs
  - async_job_manager.py - you will find everything about managing groups of async job here
  - common.py - some utils
