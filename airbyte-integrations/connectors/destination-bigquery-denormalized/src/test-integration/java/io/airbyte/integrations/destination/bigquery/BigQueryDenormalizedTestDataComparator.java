package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class BigQueryDenormalizedTestDataComparator extends AdvancedTestDataComparator {

  private static final String BIGQUERY_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'";

  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

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
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    var destinationDate = parseDateTime(actualValue);
    var expectedDate = LocalDateTime.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected boolean compareDateValues(String expectedValue, String actualValue) {
    var destinationDate = parseDate(actualValue);
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.of(LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(BIGQUERY_DATETIME_FORMAT)), ZoneOffset.UTC);
  }

  @Override
  protected boolean compareDateTimeWithTzValues(String airbyteMessageValue, String destinationValue) {
    return super.compareDateTimeWithTzValues(airbyteMessageValue, destinationValue);
  }

}
