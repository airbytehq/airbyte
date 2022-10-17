/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * A wrapper around the instantiated {@link javax.sql.DataSource}.
 *
 * Note that this class does not implement {@link AutoCloseable}/{@link java.io.Closeable}, as it is
 * not the responsibility of this class to close the provided {@link javax.sql.DataSource}. This is
 * to avoid accidentally closing a shared resource.
 */
public class AbstractDatabase {

  private JsonNode sourceConfig;
  private JsonNode databaseConfig;

  public JsonNode getSourceConfig() {
    return sourceConfig;
  }

  public void setSourceConfig(final JsonNode sourceConfig) {
    this.sourceConfig = sourceConfig;
  }

  public JsonNode getDatabaseConfig() {
    return databaseConfig;
  }

  public void setDatabaseConfig(final JsonNode databaseConfig) {
    this.databaseConfig = databaseConfig;
  }

}
