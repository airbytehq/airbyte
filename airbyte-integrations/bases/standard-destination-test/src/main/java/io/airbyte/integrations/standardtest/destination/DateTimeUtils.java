/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import com.google.common.annotations.VisibleForTesting;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoField;
import java.time.temporal.ChronoUnit;
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
              "[[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][SS][' '][z][zzz][Z][O][x][XXX][XX][X]]]");

  /**
   * Parse the Json date-time logical type to long value of epoch microseconds. Only for test
   * purposes!
   *
   * @return the number of microseconds from the unix epoch, 1 January 1970 00:00:00.000000 UTC.
   */
  @VisibleForTesting
  public static Long getEpochMicros(String jsonDateTime) {
    return convertDateTime(jsonDateTime, instant -> ChronoUnit.MICROS.between(Instant.EPOCH, instant));
  }

  /**
   * Parse the Json date logical type to int value of epoch day.
   *
   * @return the number of days from the unix epoch, 1 January 1970 (ISO calendar).
   */
  @VisibleForTesting
  public static Integer getEpochDay(String jsonDate) {
    return convertDate(jsonDate, date -> (int) date.toEpochDay());
  }

  /**
   * Parse the Json date-time type to bigquery-denormalized specific format. Only for test purposes!
   *
   * @param data "2021-01-03T01:01:01.544+01:00"
   * @return converted data "2021-01-03T01:01:01.544000"
   */
  @VisibleForTesting
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
   * Parse the Json date-time type to snowflake specific format. Only for test purposes!
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03T00:01:02Z"
   */
  @VisibleForTesting
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
   * Parse the Json date-time type to Redshift specific format. Only for test purposes!
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03 00:01:01.544000+00"
   */
  @VisibleForTesting
  public static String convertToRedshiftFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toRedshiftDateFormat);
  }

  /**
   * Parse the Json date-time type to postgres specific format. Only for test purposes!
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03T00:01:01.544Z"
   */
  @VisibleForTesting
  public static String convertToPostgresFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, Instant::toString);
  }

  /**
   * Parse the Json date-time type to databricks specific format. Only for test purposes!
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "{\"member0\":2021-01-03 00:01:01.544,\"member1\":null}"
   */
  @VisibleForTesting
  public static String convertToDatabricksFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toDatabricksDateFormat);
  }

  /**
   * Parse the Json date-time type to MSSQL specific format. Only for test purposes!
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "2021-01-03 00:01:01.544"
   */
  @VisibleForTesting
  public static String convertToMSSQLFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toMSSQLDateFormat);
  }

  /**
   * Parse the Json date type to date-time format with zero values for time. Only for test purposes!
   *
   * @param jsonDate e.g. "2021-01-01"
   * @return converted data "2021-01-01T00:00:00Z"
   */
  @VisibleForTesting
  public static String convertToDateFormatWithZeroTime(String jsonDate) {
    return convertDate(jsonDate, date -> DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'")
        .format(date.atStartOfDay().atZone(ZoneId.systemDefault())));
  }

  /**
   * Parse the Json date type to general ISO date format. Only for test purposes!
   *
   * @param jsonDate e.g. "2021-1-1"
   * @return converted data "2021-01-01"
   */
  @VisibleForTesting
  public static String convertToDateFormat(String jsonDate) {
    return convertDate(jsonDate, date -> DateTimeFormatter.ISO_LOCAL_DATE.format(
        date.atStartOfDay().atZone(ZoneId.systemDefault())));
  }

  /**
   * Verify if the value is date or date-time
   *
   * @param value any string value
   * @return true - if value is date/date-time, false - if value has any other format
   */
  public static boolean isDateTimeValue(String value) {
    try {
      ZonedDateTime.parse(value, FORMATTER);
      return true;
    } catch (DateTimeParseException ignored) {
      try {
        LocalDateTime.parse(value, FORMATTER);
        return true;
      } catch (DateTimeParseException exception) {
        try {
          LocalDate.parse(value, FORMATTER);
          return true;
        } catch (DateTimeParseException ex) {
          return false;
        }
      }
    }
  }

  /**
   * Parse the Json date type to Instant and applies function to convert instant to connector specific
   * date string. Only for test purposes!
   *
   * @param jsonDateTime input date-time string
   * @param dateTimeFormatter function to convert instant to specific date-time format string
   * @param <T> output type for date-time. Usually is String but for some cases could be a Long
   * @return converted date-time to specific format
   */
  @VisibleForTesting
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

  /**
   * Parse the Json date type to LocalDate and applies function to convert localDate to connector
   * specific date string. Only for test purposes!
   *
   * @param jsonDate input date string
   * @param dateFormatter function to convert LocalDate to specific date format string
   * @param <T> output type for date. Usually is String but for some cases could be Integer
   * @return converted date-time to specific format
   */
  @VisibleForTesting
  private static <T> T convertDate(String jsonDate, Function<LocalDate, T> dateFormatter) {
    T convertedDate = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, FORMATTER);
      convertedDate = dateFormatter.apply(date);
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return convertedDate;
  }

  /**
   * Formats instant to MSSQL date-time. Only for test purposes!
   *
   * @param instant input date-time
   * @return string with date-time without 'T' separator and zero timezone ('Z')
   */
  @VisibleForTesting
  private static String toMSSQLDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.S").withZone(ZoneOffset.UTC).format(instant);
    } else {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS").withZone(ZoneOffset.UTC).format(instant);
    }
  }

  /**
   * Formats instant to Redshift date-time. If instant has some milli of second, the output date-time
   * string will contain it after seconds, in the other case millis will be omitted for output sting.
   * Only for test purposes!
   *
   * @param instant input date-time
   * @return string with date-time with zero timezone ('+00') and without 'T' separator
   */
  @VisibleForTesting
  private static String toRedshiftDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss'+00'").withZone(ZoneOffset.UTC).format(instant);
    } else {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS'+00'").withZone(ZoneOffset.UTC).format(instant);
    }
  }

  /**
   * Formats instant to bigquery-denormalized date-time. If instant has some milli of second, the
   * output date-time string will contain it after seconds, in the other case millis will be omitted
   * for output sting. Note: bigquery-denormalized represents millis by 6-digits, but the last 3
   * digits are always '0' (e.g. 12:43:21.333000) This is the reason of division to 1000000 and then
   * multiplication to 1000 in this method Only for test purposes!
   *
   * @param instant input date-time
   * @return string with date-time without time zone
   */
  @VisibleForTesting
  private static String toBigqueryDenormalizedDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").withZone(ZoneOffset.UTC).format(instant);
    } else {
      String formattedDateTime = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS").withZone(ZoneOffset.UTC).format(instant);
      return MILLISECONDS_PATTERN.matcher(formattedDateTime).replaceAll("." + (instant.getNano() / 1000000) * 1000);
    }
  }

  /**
   * Formats instant to Databricks date-time. Only for test purposes!
   *
   * @param instant input date-time
   * @return wrapped string with date-time
   */
  @VisibleForTesting
  private static String toDatabricksDateFormat(Instant instant) {
    if (instant.get(ChronoField.MILLI_OF_SECOND) == 0) {
      return DateTimeFormatter.ofPattern(
          "'{\"member0\":'yyyy-MM-dd HH:mm:ss',\"member1\":null}'").withZone(ZoneOffset.UTC)
          .format(instant);
    } else {
      return DateTimeFormatter.ofPattern(
          "'{\"member0\":'yyyy-MM-dd HH:mm:ss.SSS',\"member1\":null}'").withZone(ZoneOffset.UTC)
          .format(instant);
    }
  }

}
