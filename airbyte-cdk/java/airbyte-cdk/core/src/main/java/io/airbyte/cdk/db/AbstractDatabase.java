/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.config.AirbyteSourceConfig;

/**
 * A wrapper around the instantiated {@link javax.sql.DataSource}.
 *
 * Note that this class does not implement {@link AutoCloseable}/{@link java.io.Closeable}, as it is
 * not the responsibility of this class to close the provided {@link javax.sql.DataSource}. This is
 * to avoid accidentally closing a shared resource.
 */
public class AbstractDatabase {

  private AirbyteSourceConfig sourceConfig;
  private JsonNode databaseConfig;

  public AirbyteSourceConfig getSourceConfig() {
    return sourceConfig;
  }

  public void setSourceConfig(final AirbyteSourceConfig sourceConfig) {
    this.sourceConfig = sourceConfig;
  }

  public JsonNode getDatabaseConfig() {
    return databaseConfig;
  }

  public void setDatabaseConfig(final JsonNode databaseConfig) {
    this.databaseConfig = databaseConfig;
  }

}
