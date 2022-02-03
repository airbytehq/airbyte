/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoField;
import java.util.Date;
import java.util.function.Function;
import java.util.regex.Pattern;
import org.apache.commons.lang3.StringUtils;

public class DateTimeUtils {

  public static final String DATE_TIME_FORMAT_PATTERN = "yyyy-MM-dd'T'HH:mm:ss'Z'";
  public static final String DATE_FORMAT_PATTERN = "yyyy-MM-dd";
  public static final DateFormat DATE_TIME_FORMAT = new SimpleDateFormat(DATE_TIME_FORMAT_PATTERN);
  public static final DateFormat DATE_FORMAT = new SimpleDateFormat(DATE_FORMAT_PATTERN);

  public static final String DATE_TIME = "date-time";
  public static final String DATE = "date";

  public static final Pattern MILLISECONDS_PATTERN = Pattern.compile("\\.\\d*");

  private static final String T_SEPARATOR = "T";
  private static final String ZERO_TIMEZONE = "Z";
  private static final DateTimeFormatter FORMATTER =
      DateTimeFormatter.ofPattern(
          "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d]" +
              "[[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]]");

  /**
   * Parse the Json date-time logical type to an Avro long value.
   *
   * @return the number of microseconds from the unix epoch, 1 January 1970 00:00:00.000000 UTC.
   */
  public static Long getEpochMicros(String jsonDateTime) {
    return convertDateTime(jsonDateTime, instant -> instant.toEpochMilli() * 1000);
  }

  /**
   * Parse the Json date logical type to an Avro int.
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
   *
   * @param data "YYYY-MM-dd HH:mm:ss"
   * @return converted data "{\"member0\":2021-01-01 01:01:01,\"member1\":null}"
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
      return DATE_TIME_FORMAT.format(new Date(instant.toEpochMilli() + instant.get(ChronoField.MILLI_OF_SECOND)));
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, FORMATTER);
        instant = dt.minusNanos(dt.getNano()).toInstant(ZoneOffset.ofHours(-8));
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  /**
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03 00:01:01.544000+00"
   */
  public static String convertToRedshiftFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toRedshiftDateFormat);
  }

  /**
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data e.g. "2021-01-03T00:01:01.544Z"
   */
  public static String convertToPostgresFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, Instant::toString);
  }

  /**
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "{\"member0\":2021-01-03 00:01:01.544,\"member1\":null}"
   */
  public static String convertToDatabricksFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toDatabricksDateFormat);
  }

  /**
   *
   * @param jsonDateTime e.g. "2021-01-03T01:01:01.544+01:00"
   * @return converted data "2021-01-03 00:01:01.544"
   */
  public static String convertToMSSQLFormat(String jsonDateTime) {
    return convertDateTime(jsonDateTime, DateTimeUtils::toMSSQLDateFormat);
  }

  /**
   *
   * @param jsonDate e.g. "2021-01-01"
   * @return converted data "2021-01-01T00:00:00Z"
   */
  public static String convertToDateFormatWithZeroTime(String jsonDate) {
    return convertDate(jsonDate, date -> DATE_TIME_FORMAT.format(
        Date.from(date.atStartOfDay().atZone(ZoneId.systemDefault()).toInstant())));
  }

  /**
   *
   * @param jsonDate e.g. "2021-1-1"
   * @return converted data "2021-01-01"
   */
  public static String convertToDateFormat(String jsonDate) {
    return convertDate(jsonDate, date -> DATE_FORMAT.format(
        Date.from(date.atStartOfDay().atZone(ZoneId.systemDefault()).toInstant())));
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
    String str = MILLISECONDS_PATTERN.matcher(instant.toString().replace(T_SEPARATOR, StringUtils.SPACE)
        .replace(ZERO_TIMEZONE, StringUtils.EMPTY))
        .replaceAll("." + (instant.get(ChronoField.MILLI_OF_SECOND) == 0 ? "0"
            : (instant.get(ChronoField.MICRO_OF_SECOND) + 500) / 1000));
    return instant.get(ChronoField.MILLI_OF_SECOND) > 0 ? str : str + ".0";
  }

  private static String toRedshiftDateFormat(Instant instant) {
    return MILLISECONDS_PATTERN.matcher(instant.toString().replace(T_SEPARATOR, StringUtils.SPACE).replace(ZERO_TIMEZONE, "+00"))
        .replaceAll("." + instant.get(ChronoField.MICRO_OF_SECOND));
  }

  private static String toBigqueryDenormalizedDateFormat(Instant instant) {
    return MILLISECONDS_PATTERN.matcher(instant.toString().replace(ZERO_TIMEZONE, StringUtils.EMPTY))
        .replaceAll("." + (instant.getNano() / 1000000) * 1000);
  }

  private static String toDatabricksDateFormat(Instant instant) {
    return String.format("***\"member0\":%s,\"member1\":null***", MILLISECONDS_PATTERN.matcher(instant.toString().replace('T', ' ').replace("Z", ""))
        .replaceAll("." + instant.get(ChronoField.MICRO_OF_SECOND) / 1000));
  }

}
