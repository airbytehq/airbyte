FROM postgres:11-alpine

COPY server.key /var/lib/postgresql/server.key
COPY server.crt /var/lib/postgresql/server.crt

# update the privileges on the .key, no need to touch the .crt
RUN chmod 600 /var/lib/postgresql/server.key
RUN chown postgres:postgres /var/lib/postgresql/server.key
