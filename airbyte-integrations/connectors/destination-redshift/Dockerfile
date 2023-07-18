### WARNING ###
# The Java connector Dockerfiles will soon be deprecated.
# This Dockerfile is not used to build the connector image we publish to DockerHub.
# The new logic to build the connector image is declared with Dagger here:
# https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/environments.py#L649

# If you need to add a custom logic to build your connector image, you can do it by adding a finalize_build.sh or finalize_build.py script in the connector folder.
# Please reach out to the Connectors Operations team if you have any question.
FROM airbyte/integration-base-java:dev AS build

# amazon linux 2 isn't compatible with urllib3 2.x, so force 1.26.15
RUN yum install -y python3 python3-devel jq sshpass git && yum clean all && \
  alternatives --install /usr/bin/python python /usr/bin/python3 60 && \
  python -m ensurepip --upgrade && \
  pip3 install dbt-redshift==1.0.0 "urllib3<2"

# Luckily, none of normalization's files conflict with destination-bigquery's files :)
# We don't enforce that in any way, but hopefully we're only living in this state for a short time.
COPY --from=airbyte/normalization-redshift:dev /airbyte /airbyte
# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip3 install .
WORKDIR /airbyte/normalization_code
RUN pip3 install .
WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte

ENV APPLICATION destination-redshift
ENV AIRBYTE_NORMALIZATION_INTEGRATION redshift

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-redshift

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.6.1
LABEL io.airbyte.name=airbyte/destination-redshift

ENV AIRBYTE_ENTRYPOINT "/airbyte/run_with_normalization.sh"
ENTRYPOINT ["/airbyte/run_with_normalization.sh"]
