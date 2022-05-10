/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;

public abstract class AbstractDatabase {

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
