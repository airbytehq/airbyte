# Pinecone Migration Guide

## Upgrading to 1.0.0

This version introduces `Default Namespace` config, which provides a fallback namespace to write into when you don't define a namespace in the connection settings.

Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.
