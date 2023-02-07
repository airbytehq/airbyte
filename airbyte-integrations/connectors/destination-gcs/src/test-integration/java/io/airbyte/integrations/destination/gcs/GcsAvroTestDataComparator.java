/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.nio.charset.StandardCharsets;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.Base64;

public class GcsAvroTestDataComparator extends AdvancedTestDataComparator {

  @Override
  protected boolean compareDateValues(String expectedValue, String actualValue) {
    LocalDate destinationDate = LocalDate.ofEpochDay(Long.parseLong(actualValue));
    LocalDate expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  private Instant getInstantFromEpoch(String epochValue) {
    return Instant.ofEpochMilli(Long.parseLong(epochValue) / 1000);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
  }

  @Override
  protected boolean compareDateTimeValues(String airbyteMessageValue, String destinationValue) {
    DateTimeFormatter format = DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT);
    LocalDateTime dateTime = LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    return super.compareDateTimeValues(airbyteMessageValue, format.format(dateTime));
  }

  @Override
  protected boolean compareTimeWithoutTimeZone(final String airbyteMessageValue, final String destinationValue) {
    LocalTime destinationDate = LocalTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    LocalTime expectedDate = LocalTime.parse(airbyteMessageValue, DateTimeFormatter.ISO_TIME);
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected boolean compareString(final JsonNode expectedValue, final JsonNode actualValue) {
    // to handle base64 encoded strings
    return expectedValue.asText().equals(actualValue.asText())
        || decodeBase64(expectedValue.asText()).equals(actualValue.asText());
  }

  private String decodeBase64(String string) {
    byte[] decoded = Base64.getDecoder().decode(string);
    return new String(decoded, StandardCharsets.UTF_8);
  }

}
