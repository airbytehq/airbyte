/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

public class SnowflakeInternalStagingRawSchemaOverrideTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_internal_staging_config_raw_schema_override.json";
  }

  @Override
  protected String getRawSchema() {
    return "overridden_raw_dataset";
  }

}
