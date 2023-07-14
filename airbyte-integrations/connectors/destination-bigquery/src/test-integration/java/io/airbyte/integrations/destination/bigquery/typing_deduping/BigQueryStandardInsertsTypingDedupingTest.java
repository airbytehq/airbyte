package io.airbyte.integrations.destination.bigquery.typing_deduping;

public class BigQueryStandardInsertsTypingDedupingTest extends AbstractBigQueryTypingDedupingTest {

  @Override
  public String getConfigPath() {
    return "secrets/credentials-1s1t-standard.json";
  }
}
