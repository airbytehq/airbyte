/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.utils;

public enum ConnectorType {

  MYSQL,
  MSSQL,
  POSTGRES,
  ORACLE,
  MONGO,
  SNOWFLAKE,
  REDSHIFT,
  GCS,
  DEFAULT
}
