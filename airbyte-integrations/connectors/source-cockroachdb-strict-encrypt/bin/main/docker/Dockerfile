FROM cockroachdb/cockroach:v20.2.18

##
# Test CockroachDB container with enabled SSL
# Database: defaultdb
# User: test_user
# Build command: docker build -f Dockerfile -t cockroachdb-test-ssl:latest .
# Run command: docker run -td -p 26257:26257 -p 8080:8080 --name cockroach-test-cont  cockroachdb-test-ssl:latest
##

ENV COCKROACH_HOST localhost:26257
ENV COCKROACH_CERTS_DIR certs

EXPOSE 8080
EXPOSE 26257

COPY cockroachdb_init.sh .
COPY cockroachdb_test_user.sh .

RUN chmod +x cockroachdb_init.sh

ENTRYPOINT cockroachdb_init.sh
