package io.airbyte.integrations.destination.snowflake.typing_deduping;

public class SnowflakeGcsStagingTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {
  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_copy_gcs_config.json";
  }
}
