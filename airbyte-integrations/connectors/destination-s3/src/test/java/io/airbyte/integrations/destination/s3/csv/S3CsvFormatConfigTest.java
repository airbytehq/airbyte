package io.airbyte.integrations.destination.s3.csv;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3CsvFormatConfig")
public class S3CsvFormatConfigTest {

  @Test
  @DisplayName("Flattening enums can be created from value string")
  public void testFlatteningCreationFromString() {
    assertEquals(Flattening.NO, Flattening.fromValue("no flattening"));
    assertEquals(Flattening.ROOT_LEVEL, Flattening.fromValue("root level flattening"));
  }

}
