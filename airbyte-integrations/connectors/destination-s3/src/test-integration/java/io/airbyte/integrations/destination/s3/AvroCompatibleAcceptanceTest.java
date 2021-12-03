package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import tech.allegro.schema.json2avro.converter.util.DateTimeUtils;

public abstract class AvroCompatibleAcceptanceTest extends S3DestinationAcceptanceTest {

  protected AvroCompatibleAcceptanceTest(final S3Format outputFormat) {
    super(outputFormat);
  }

  @Override
  protected void assertSameValue(final String key, final JsonNode expectedValue, final JsonNode actualValue) {
    if (key.equals("date")) {
      assertEquals(parseDateValue(expectedValue), parseDateValue(actualValue));
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

  /**
   * All dates are converted to yyyyMMdd for comparison, because it is relatively
   * easy to convert yyyy-MM-dd or epoch day to this format than the other way around.
   */
  private String parseDateValue(final JsonNode value) {
    if (value.isNumber()) {
      return LocalDate.ofEpochDay(value.asInt()).format(DateTimeFormatter.ofPattern("yyyyMMdd"));
    }

    final Integer epochDay = DateTimeUtils.getEpochDay(value.asText());
    if (epochDay != null) {
      return LocalDate.ofEpochDay(epochDay).format(DateTimeFormatter.ofPattern("yyyyMMdd"));
    }

    // remove "-" in yyyy-MM-dd
    return value.textValue().replaceAll("-\"", "");
  }

}
