/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import java.util.Map;

/**
 * By default, the input schema of a migration should be the output schema of the previous
 * migration. This base class enforces this rule.
 */
public abstract class BaseMigration implements Migration {

  private final Migration previousMigration;

  public BaseMigration(Migration previousMigration) {
    this.previousMigration = previousMigration;
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    return previousMigration.getOutputSchema();
  }

}
