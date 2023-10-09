# Jira Migration Guide

# 1.0.0
The types for `aggegatetimeoriginalestimate` and `timeoriginalestimate` in the `issues` stream have been changed to `string`. You may need to refresh the connection schema for this stream (skipping the reset), and running a sync. Alternatively, you can just run a reset.
