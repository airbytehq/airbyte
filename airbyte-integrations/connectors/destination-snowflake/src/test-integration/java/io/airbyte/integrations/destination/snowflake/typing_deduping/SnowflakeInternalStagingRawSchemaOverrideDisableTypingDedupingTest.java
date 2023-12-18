/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

public class SnowflakeInternalStagingRawSchemaOverrideDisableTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_disabletd_internal_staging_config_raw_schema_override.json";
  }

  @Override
  protected String getRawSchema() {
    return "overridden_raw_dataset";
  }

  @Override
  protected boolean disableFinalTableComparison() {
    return true;
  }

  @Override
  public void testRemovingPKNonNullIndexes() throws Exception {
    // Do nothing.
  }

  @Override
  public void identicalNameSimultaneousSync() throws Exception {
    // TODO: create fixtures to verify how raw tables are affected. Base tests check for final tables.
  }

}
