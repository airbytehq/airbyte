# Pardot Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 adds 23 new streams, and migrates all existing streams to the new V5 Pardot API.

The previous implementation of the authentication flow was no longer functional, preventing syncs.
The auth flow has been fixed. Any users with existing connections should reconfigure their source and run through the authentication setup.
