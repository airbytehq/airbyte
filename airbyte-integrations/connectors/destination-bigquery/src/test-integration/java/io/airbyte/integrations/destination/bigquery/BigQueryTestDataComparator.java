/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryTestDataComparator extends AdvancedTestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryTestDataComparator.class);
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private static final String BIGQUERY_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'";

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    result.add(namingResolver.getIdentifier(identifier));
    return result;
  }

  private LocalDate parseDate(String dateValue) {
    if (dateValue != null) {
      var format = (dateValue.matches(".+Z") ? BIGQUERY_DATETIME_FORMAT : AIRBYTE_DATE_FORMAT);
      return LocalDate.parse(dateValue, DateTimeFormatter.ofPattern(format));
    } else {
      return null;
    }
  }

  private LocalDateTime parseDateTime(String dateTimeValue) {
    if (dateTimeValue != null) {
      var format = (dateTimeValue.matches(".+Z") ? BIGQUERY_DATETIME_FORMAT : AIRBYTE_DATETIME_FORMAT);
      return LocalDateTime.parse(dateTimeValue, DateTimeFormatter.ofPattern(format));
    } else {
      return null;
    }
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    if (destinationValue != null) {
      if (destinationValue.matches(".+Z")) {
        return ZonedDateTime.of(LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(BIGQUERY_DATETIME_FORMAT)), ZoneOffset.UTC);
      } else {
        return ZonedDateTime.parse(destinationValue, getAirbyteDateTimeWithTzFormatter()).withZoneSameInstant(ZoneOffset.UTC);
      }
    } else {
      return null;
    }
  }

  @Override
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    var destinationDate = parseDateTime(actualValue);
    var expectedDate = LocalDateTime.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    // #13123 Normalization issue
    if (expectedDate.isBefore(getBrokenDate().toLocalDateTime())) {
      LOGGER
          .warn("Validation is skipped due to known Normalization issue. Values older then 1583 year and with time zone stored wrongly(lose days).");
      return true;
    } else {
      return expectedDate.equals(destinationDate);
    }
  }

  @Override
  protected boolean compareDateValues(String expectedValue, String actualValue) {
    var destinationDate = parseDate(actualValue);
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected boolean compareDateTimeWithTzValues(String airbyteMessageValue, String destinationValue) {
    // #13123 Normalization issue
    if (parseDestinationDateWithTz(destinationValue).isBefore(getBrokenDate())) {
      LOGGER
          .warn("Validation is skipped due to known Normalization issue. Values older then 1583 year and with time zone stored wrongly(lose days).");
      return true;
    } else {
      return super.compareDateTimeWithTzValues(airbyteMessageValue, destinationValue);
    }
  }

  // #13123 Normalization issue
  private ZonedDateTime getBrokenDate() {
    return ZonedDateTime.of(1583, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC);
  }

  @Override
  protected void compareObjects(JsonNode expectedObject, JsonNode actualObject) {
    JsonNode actualJsonNode = (actualObject.isTextual() ? Jsons.deserialize(actualObject.textValue()) : actualObject);
    super.compareObjects(expectedObject, actualJsonNode);
  }

}
