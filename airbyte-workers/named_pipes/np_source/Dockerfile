FROM alpine:latest
COPY run.sh /tmp/run.sh
ENV AIRBYTE_ENTRYPOINT=">&2 /tmp/run.sh"
ENTRYPOINT [">&2", "/tmp/run.sh"]
