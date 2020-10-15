#!/usr/bin/env sh

# copy seed data over if the seed mount is empty. if it is not, we assume
# that it is already seeded and should not be overwritten.
[ "$(ls -A /seed )" ] || cp -r /app/seed/* /seed
