package io.airbyte.integrations.destination.redshift.typing_deduping;

public class RedshiftS3StagingTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {
  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_config_staging.json";
  }
}
