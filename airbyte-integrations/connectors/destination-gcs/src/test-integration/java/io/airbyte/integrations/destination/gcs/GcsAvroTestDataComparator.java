/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.*;
import java.time.format.DateTimeFormatter;

public class GcsAvroTestDataComparator extends AdvancedTestDataComparator {

  @Override
  protected boolean compareDateValues(String expectedValue, String actualValue) {
    var destinationDate = LocalDate.ofEpochDay(Long.parseLong(actualValue));
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  private Instant getInstantFromEpoch(String epochValue) {
    return Instant.ofEpochMilli(Long.parseLong(epochValue.replaceAll("000$", "")));
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
  }

  @Override
  protected boolean compareDateTimeValues(String airbyteMessageValue, String destinationValue) {
    var format = DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT);
    LocalDateTime dateTime = LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    return super.compareDateTimeValues(airbyteMessageValue, format.format(dateTime));
  }

}
