package io.airbyte.integrations.destination.snowflake.typing_deduping;

import org.junit.jupiter.api.Disabled;

@Disabled
public class SnowflakeS3StagingTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {
  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_copy_s3_config.json";
  }
}
