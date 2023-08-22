package io.airbyte.integrations.destination.bigquery.typing_deduping;

public class BigQueryStandardInsertsRawOverrideTypingDedupingTest extends AbstractBigQueryTypingDedupingTest {

  @Override
  public String getConfigPath() {
    return "secrets/credentials-1s1t-standard-raw-override.json";
  }

  @Override
  protected String getRawDataset() {
    return "overridden_raw_dataset";
  }
}
