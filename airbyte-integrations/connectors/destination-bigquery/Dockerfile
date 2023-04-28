FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-bigquery

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

RUN yum install -y python3 python3-devel jq sshpass git && \
  alternatives --install /usr/bin/python python /usr/bin/python3 60 && \
  python -m ensurepip --upgrade && \
  pip3 install dbt-bigquery==1.0.0

# Luckily, none of normalization's files conflict with destination-bigquery's files :)
# We don't enforce that in any way, but hopefully we're only living in this state for a short time.
COPY --from=airbyte/normalization:dev /airbyte /airbyte
# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip3 install .
WORKDIR /airbyte/normalization_code
RUN pip3 install .
WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte

ENV APPLICATION destination-bigquery
ENV AIRBYTE_NORMALIZATION_INTEGRATION bigquery

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=1.3.4
LABEL io.airbyte.name=airbyte/destination-bigquery

ENV AIRBYTE_ENTRYPOINT "/airbyte/run_with_normalization.sh"
ENTRYPOINT ["/airbyte/run_with_normalization.sh"]
