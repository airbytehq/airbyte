package io.airbyte.integrations.destination.snowflake.typing_deduping;

import org.junit.jupiter.api.Disabled;

@Disabled
public class SnowflakeInternalStagingTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {
  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_internal_staging_config.json";
  }
}
