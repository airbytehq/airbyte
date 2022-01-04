#!/usr/bin/env bash

. tools/lib/lib.sh

# Whoever runs this script must accept the following terms & conditions:
# https://databricks.com/jdbc-odbc-driver-license
_get_databricks_jdbc_driver() {
  local driver_zip="SimbaSparkJDBC42-2.6.21.1039.zip"
  local driver_url="https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/jdbc/2.6.21/${driver_zip}"
  local connector_path="airbyte-integrations/connectors/destination-databricks"

  if [[ -f "${connector_path}/lib/SparkJDBC42.jar" ]] ; then
    echo "[Databricks] Spark JDBC driver already exists"
  else
    echo "[Databricks] Downloading Spark JDBC driver..."
    curl -o "${connector_path}/lib/SimbaSparkJDBC42-2.6.21.1039.zip" "${driver_url}"
    tar -xf "${connector_path}/lib/SimbaSparkJDBC42-2.6.21.1039.zip" SparkJDBC42.jar
    mv SparkJDBC42.jar "${connector_path}/lib/"
    rm "${connector_path}/lib/SimbaSparkJDBC42-2.6.21.1039.zip"
  fi
}
