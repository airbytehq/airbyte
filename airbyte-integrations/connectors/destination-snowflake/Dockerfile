### WARNING ###
# The Java connector Dockerfiles will soon be deprecated.
# This Dockerfile is not used to build the connector image we publish to DockerHub.
# The new logic to build the connector image is declared with Dagger here:
# https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/environments.py#L649

# If you need to add a custom logic to build your connector image, you can do it by adding a finalize_build.sh or finalize_build.py script in the connector folder.
# Please reach out to the Connectors Operations team if you have any question.
FROM airbyte/integration-base-java:dev

# uncomment to run Yourkit java profiling
#RUN yum install -y curl zip
#
#RUN curl -o /tmp/YourKit-JavaProfiler-2021.3-docker.zip https://www.yourkit.com/download/docker/YourKit-JavaProfiler-2021.3-docker.zip && \
#  unzip /tmp/YourKit-JavaProfiler-2021.3-docker.zip -d /usr/local && \
#  rm /tmp/YourKit-JavaProfiler-2021.3-docker.zip

# amazon linux 2 isn't compatible with urllib3 2.x, so force 1.26.15
RUN yum install -y python3 python3-devel jq sshpass git gcc-c++ && yum clean all && \
  alternatives --install /usr/bin/python python /usr/bin/python3 60 && \
  python -m ensurepip --upgrade && \
  pip3 install dbt-snowflake==1.0.0 "urllib3<2"

COPY --from=airbyte/normalization-snowflake:dev /airbyte /airbyte
# Install python dependencies
WORKDIR /airbyte/base_python_structs
RUN pip3 install .
WORKDIR /airbyte/normalization_code
RUN pip3 install .
WORKDIR /airbyte/normalization_code/dbt-template/
# Download external dbt dependencies
RUN dbt deps

WORKDIR /airbyte

ENV APPLICATION destination-snowflake
ENV AIRBYTE_NORMALIZATION_INTEGRATION snowflake

# Needed for JDK17 (in turn, needed on M1 macs) - see https://github.com/snowflakedb/snowflake-jdbc/issues/589#issuecomment-983944767
ENV DESTINATION_SNOWFLAKE_OPTS "--add-opens java.base/java.nio=ALL-UNNAMED"

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1

ENV ENABLE_SENTRY true


LABEL io.airbyte.version=1.2.1
LABEL io.airbyte.name=airbyte/destination-snowflake

ENV AIRBYTE_ENTRYPOINT "/airbyte/run_with_normalization.sh"
ENTRYPOINT ["/airbyte/run_with_normalization.sh"]
