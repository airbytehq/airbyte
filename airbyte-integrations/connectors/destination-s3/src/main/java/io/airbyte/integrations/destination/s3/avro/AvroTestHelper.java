package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import tech.allegro.schema.json2avro.converter.util.DateTimeUtils;

public class AvroTestHelper {

  public static void assertDate(final JsonNode expectedValue, final JsonNode actualValue) {
    assertEquals(parseDateValue(expectedValue), parseDateValue(actualValue));
  }

  /**
   * All dates are converted to yyyyMMdd for comparison, because it is relatively
   * easy to convert yyyy-MM-dd or epoch day to this format than the other way around.
   */
  public static String parseDateValue(final JsonNode value) {
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
