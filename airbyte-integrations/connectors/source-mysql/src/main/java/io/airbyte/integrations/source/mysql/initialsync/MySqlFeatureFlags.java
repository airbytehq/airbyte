/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;

// Feature flags to gate new primary key load features.
public class MySqlFeatureFlags {

  private final JsonNode sourceConfig;

  public MySqlFeatureFlags(final JsonNode sourceConfig) {
    this.sourceConfig = sourceConfig;
  }

  private boolean getFlagValue(final String flag) {
    return sourceConfig.has(flag) && sourceConfig.get(flag).asBoolean();
  }

}
