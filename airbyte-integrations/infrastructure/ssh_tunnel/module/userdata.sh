#!/bin/bash -e

# Apply security patches
sudo yum update -y

# TODO: Figure out if connectors should use password auth or ssh keys for this, or support both.

