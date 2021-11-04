#!/usr/bin/env bash

. tools/lib/lib.sh

# Download Spark JDBC driver for the Databricks destination.
# The original driver file was downloaded from
# https://databricks.com/spark/jdbc-drivers-download
# with the acceptance to the terms & conditions.
_get_databricks_jdbc_driver() {
  local connector_path="airbyte-integrations/connectors/destination-databricks"

  if [[ -f "$connector_path"/lib/SparkJDBC42.jar ]] ; then
    echo "[Databricks] Spark JDBC driver already exists"
  else
    echo "[Databricks] Downloading Spark JDBC driver..."
    gsutil cp gs://io-airbyte-build-dependencies/SparkJDBC42.jar "$connector_path"/lib
  fi
}
