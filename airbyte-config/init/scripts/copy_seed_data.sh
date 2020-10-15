#!/usr/bin/env sh

# this is written as a script, despite its simplicity, because the yaml parser freaks out if $
# is used for anything but variable interpolation.

set -e

# copy seed data over if the seed mount is empty. if it is not, we assume
# that it is already seeded and should not be overwritten.
[ "$(ls -A /seed )" ] || cp -r /app/seed/* /seed
