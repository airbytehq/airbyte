/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoField;
import java.util.function.Function;
import java.util.regex.Pattern;

/**
 * Used for operations on date/date-time strings to convert it to the specific connector's format
 * Only for test purposes.
 */
public class DateTimeUtils {

  public static final String DATE_TIME_FORMAT_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'";

  public static final String DATE_TIME = "date-time";
  public static final String DATE = "date";

  public static final Pattern MILLISECONDS_PATTERN = Pattern.compile("\\.\\d*");

  private static final DateTimeFormatter FORMATTER =
      DateTimeFormatter.ofPattern(
          "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d]" +
              "[[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]]");

  /**
   * Parse the Json date-time logical type to long value of epoch microseconds.
   *
   * @return the number of microseconds from the unix epoch, 1 January 1970 00:00:00.000000 UTC.
   */
  public static Long getEpochMicros(String jsonDateTime) {
    return convertDateTime(jsonDateTime, instant -> instant.toEpochMilli() * 1000);
  }

  /**
   * Parse the Json date logical type to int value of epoch day.
   *
   * @return the number of days from the unix epoch, 1 January 1970 (ISO calendar).
   */
  public static Integer getEpochDay(String jsonDate) {
    Integer epochDay = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, FORMATTER);
      epochDay = (int) date.toEpochDay();
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return epochDay;
  }

  /**
   * Parse the Json date-time type to bigquery-denormalized specific format.
   *
   * @param data "2021-01-03T01:01:01.544+01:00"
   * @return converted data "2021-01-03T01:01:01.544000"
   */
  public static String convertToBigqueryDenormalizedFormat(String data) {
    Instant instant = null;
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(data, FORMATTER);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.UTC);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(data, FORMATTER);
        instant = dt.toInstant(ZoneOffset.UTC);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : toBigqueryDenormalizedDateFormat(instant);
  }

  /**
   * Parse the Json date-time type to snowflake specific format
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03T00:01:02Z"
   */
  public static String convertToSnowflakeFormat(String jsonDateTime) {
    Instant instant = null;
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, FORMATTER);
      instant = zdt.toLocalDateTime().atZone(ZoneId.systemDefault()).toLocalDateTime()
          .toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return DateTimeFormatter.ofPattern(DATE_TIME_FORMAT_PATTERN).withZone(ZoneOffset.UTC).format(instant);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, FORMATTER);
        instant = dt.toInstant(ZoneOffset.ofHours(-8));
        return DateTimeFormatter.ofPattern(DATE_TIME_FORMAT_PATTERN).withZone(ZoneOffset.UTC).format(instant);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  /**
   * Parse the Json date-time type to Redshift specific format
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03 00:01:01.544000+00"
   */
  public static String convertToRedshiftFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toRedshiftDateFormat);
  }

  /**
   * Parse the Json date-time type to postgres specific format
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03T00:01:01.544Z"
   */
  public static String convertToPostgresFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, Instant::toString);
  }

  /**
   * Parse the Json date-time type to databricks specific format
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "{\"member0\":2021-01-03 00:01:01.544,\"member1\":null}"
   */
  public static String convertToDatabricksFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toDatabricksDateFormat);
  }

  /**
   * Parse the Json date-time type to MSSQL specific format
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "2021-01-03 00:01:01.544"
   */
  public static String convertToMSSQLFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toMSSQLDateFormat);
  }

  /**
   * Parse the Json date type to date-time format with zero values for time
   *
   * @param jsonDate e.g. "2021-01-01"
   * @return converted data "2021-01-01T00:00:00Z"
   */
  public static String convertToDateFormatWithZeroTime(String jsonDate) {
    return convertDate(jsonDate, date -> DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'")
        .format(date.atStartOfDay().atZone(ZoneId.systemDefault())));
  }

  /**
   * Parse the Json date type to general ISO date format
   *
   * @param jsonDate e.g. "2021-1-1"
   * @return converted data "2021-01-01"
   */
  public static String convertToDateFormat(String jsonDate) {
    return convertDate(jsonDate, date -> DateTimeFormatter.ISO_LOCAL_DATE.format(
        date.atStartOfDay().atZone(ZoneId.systemDefault())));
  }

  private static <T> T convertDateTime(String jsonDateTime, Function<Instant, T> dateTimeFormatter) {
    Instant instant = null;
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, FORMATTER);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, FORMATTER);
        instant = dt.toInstant(ZoneOffset.UTC);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : dateTimeFormatter.apply(instant);
  }

  private static String convertDate(String jsonDate, Function<LocalDate, String> dateFormatter) {
    String convertedDate = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, FORMATTER);
      convertedDate = dateFormatter.apply(date);
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return convertedDate;
  }

  private static String toMSSQLDateFormat(Instant instant) {
    return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS").withZone(ZoneOffset.UTC).format(instant);
  }

  private static String toRedshiftDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss'+00'").withZone(ZoneOffset.UTC).format(instant);
    } else {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS'+00'").withZone(ZoneOffset.UTC).format(instant);
    }
  }

  private static String toBigqueryDenormalizedDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").withZone(ZoneOffset.UTC).format(instant);
    } else {
      String formattedDateTime = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS").withZone(ZoneOffset.UTC).format(instant);
      return MILLISECONDS_PATTERN.matcher(formattedDateTime).replaceAll("." + (instant.getNano() / 1000000) * 1000);
    }
  }

  private static String toDatabricksDateFormat(Instant instant) {
    return DateTimeFormatter.ofPattern("'***\"member0\":'yyyy-MM-dd HH:mm:ss.SSS',\"member1\":null***'").withZone(ZoneOffset.UTC).format(instant);
  }

}
