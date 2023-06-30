package io.airbyte.integrations.destination.bigquery.typing_deduping;

import java.io.IOException;
import org.junit.jupiter.api.BeforeAll;

public class BigQueryStandardInsertsTypingDedupingTest extends AbstractBigQueryTypingDedupingTest {

  // Note that this is not an @Override, because it's a static method. I would love suggestions on how to do this better :)
  @BeforeAll
  public static void buildConfig() throws IOException {
    setConfig("secrets/credentials-1s1t-standard.json");
  }
}
