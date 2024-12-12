# Pardot Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 adds 23 new streams, and migrates all existing streams (minus `email_clicks`) to V5 of the Pardot API.

The previous implementation of the authentication flow was no longer functional, preventing the instantiation of new sources.
The auth flow has now been fixed, enabling new connections on Cloud. Any users with existing connections should reconfigure their source and run through the authentication setup.
