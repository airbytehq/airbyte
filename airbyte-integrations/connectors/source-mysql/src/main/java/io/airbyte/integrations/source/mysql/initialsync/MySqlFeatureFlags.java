/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;

// Feature flags to gate new primary key load features.
public class MySqlFeatureFlags {

  public static final String STANDARD_VIA_PK = "standard_via_pk";
  private final JsonNode sourceConfig;

  public MySqlFeatureFlags(final JsonNode sourceConfig) {
    this.sourceConfig = sourceConfig;
  }

  public boolean isStandardInitialSyncViaPkEnabled() {
    return getFlagValue(STANDARD_VIA_PK);
  }

  private boolean getFlagValue(final String flag) {
    return sourceConfig.has(flag) && sourceConfig.get(flag).asBoolean();
  }

}
