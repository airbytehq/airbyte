/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class S3BaseAvroParquetTestDataComparator extends AdvancedTestDataComparator {

  @Override
  protected boolean compareDateValues(String airbyteMessageValue, String destinationValue) {
    var destinationDate = LocalDate.ofEpochDay(Long.parseLong(destinationValue));
    var expectedDate = LocalDate.parse(airbyteMessageValue, DateTimeFormatter.ofPattern(AdvancedTestDataComparator.AIRBYTE_DATE_FORMAT));
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
    var format = DateTimeFormatter.ofPattern(AdvancedTestDataComparator.AIRBYTE_DATETIME_FORMAT);
    LocalDateTime dateTime = LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC);
    return super.compareDateTimeValues(airbyteMessageValue, format.format(dateTime));
  }

}
