package io.airbyte.integrations.destination.bigquery.typing_deduping;

import java.io.IOException;
import org.junit.jupiter.api.BeforeAll;

public class BigQueryGcsTypingDedupingTest extends AbstractBigQueryTypingDedupingTest {

  @BeforeAll
  public static void buildConfig() throws IOException {
    setConfig("secrets/credentials-1s1t-gcs.json");
  }
}
