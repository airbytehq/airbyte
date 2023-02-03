/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Base64;

public class S3AvroParquetTestDataComparator extends AdvancedTestDataComparator {

  @Override
  protected boolean compareDateValues(String airbyteMessageValue, String destinationValue) {
    var destinationDate = LocalDate.ofEpochDay(Long.parseLong(destinationValue));
    var expectedDate = LocalDate.parse(airbyteMessageValue, DateTimeFormatter.ISO_LOCAL_DATE);
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
    LocalDateTime destinationDate = LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    return super.compareDateTimeValues(airbyteMessageValue, destinationDate.toString());
  }

  @Override
  protected boolean compareTimeWithoutTimeZone(final String airbyteMessageValue, final String destinationValue) {
    var destinationDate = LocalTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    var expectedDate = LocalTime.parse(airbyteMessageValue, DateTimeFormatter.ISO_TIME);
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
