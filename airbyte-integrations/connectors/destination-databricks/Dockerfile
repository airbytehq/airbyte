FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-databricks

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar
RUN if [ -f "lib/SparkJDBC42.jar" ]; then \
    echo "[Databricks] JDBC driver exists"; \
  else \
    echo "[Databricks] JDBC drier does not exist"; \
    apt-get update && apt-get install -y unzip curl; \
    driver_zip="SimbaSparkJDBC42-2.6.21.1039.zip"; \
    driver_file="SparkJDBC42.jar"; \
    driver_url="https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/jdbc/2.6.21/${driver_zip}"; \
    echo "[Databricks] Downloading JDBC driver to lib/${driver_zip}..."; \
    curl -o "lib/${driver_zip}" "${driver_url}"; \
    echo "[Databricks] Extracting JDBC driver file ${driver_file}..."; \
    unzip "lib/${driver_zip}" "${driver_file}"; \
    echo "[Databricks] Moving ${driver_file} to lib/"; \
    mv "${driver_file}" "lib/"; \
    rm "lib/${driver_zip}"; \
  fi

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-databricks

COPY --from=build /airbyte /airbyte

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/destination-databricks
