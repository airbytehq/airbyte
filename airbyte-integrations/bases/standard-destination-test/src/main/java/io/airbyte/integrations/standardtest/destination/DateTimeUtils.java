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
import java.util.Date;
import java.util.regex.Pattern;

public class DateTimeUtils {

  public static final String DATE_TIME_FORMAT_PATTERN = "yyyy-MM-dd'T'HH:mm:ss'Z'";
  public static final String DATE_FORMAT_PATTERN = "yyyy-MM-dd";
  public static final DateFormat DATE_TIME_FORMAT = new SimpleDateFormat(DATE_TIME_FORMAT_PATTERN);
  public static final DateFormat DATE_FORMAT = new SimpleDateFormat(DATE_FORMAT_PATTERN);

  public static final String DATE_TIME = "date-time";
  public static final String DATE = "date";

  public static final Pattern MILLISECONDS_PATTERN = Pattern.compile("\\.\\d*");

  private static final DateTimeFormatter formatter =
      DateTimeFormatter.ofPattern(
          "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d]" +
              "[[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]]");

  /**
   * Parse the Json date-time logical type to an Avro long value.
   *
   * @return the number of microseconds from the unix epoch, 1 January 1970 00:00:00.000000 UTC.
   */
  public static Long getEpochMicros(String jsonDateTime) {
    Instant instant = null;
    if (jsonDateTime.matches("-?\\d+")) {
      return Long.valueOf(jsonDateTime);
    }
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toEpochMilli() * 1000;
  }

  /**
   * Parse the Json date logical type to an Avro int.
   *
   * @return the number of days from the unix epoch, 1 January 1970 (ISO calendar).
   */
  public static Integer getEpochDay(String jsonDate) {
    Integer epochDay = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, formatter);
      epochDay = (int) date.toEpochDay();
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return epochDay;
  }

  public static String convertToBigqueryDenormalizedFormat(String data) {
    Instant instant = null;
    try {

      ZonedDateTime zdt = ZonedDateTime.parse(data, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.UTC);
      return toBigqueryDenormalizedDateFormat(instant);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(data, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
        return toBigqueryDenormalizedDateFormat(instant);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToSnowflakeFormat(String jsonDateTime) {
    Instant instant = null;
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().atZone(ZoneId.systemDefault()).toLocalDateTime()
          .toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return DATE_TIME_FORMAT.format(new Date(instant.toEpochMilli() + (instant.getNano() / 1000000)));
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.minusNanos(dt.getNano()).toInstant(ZoneOffset.ofHours(-8));
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToRedshiftFormat(String jsonDateTime) {
    Instant instant = null;
    try {

      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return toRedshiftDateFormat(instant);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
        return toRedshiftDateFormat(instant);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToPostgresFormat(String jsonDateTime) {
    Instant instant = null;
    try {

      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return instant.toString();
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
        return instant.toString();
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToDatabricksFormat(String jsonDateTime) {
    Instant instant = null;
    try {

      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return toDatabricksDateFormat(instant);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
        return toDatabricksDateFormat(instant);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToMSSQLFormat(String jsonDateTime) {
    Instant instant = null;
    try {
      ZonedDateTime zdt = ZonedDateTime.parse(jsonDateTime, formatter);
      instant = zdt.toLocalDateTime().toInstant(ZoneOffset.of(zdt.getOffset().toString()));
      return toMSSQLDateFormat(instant);
    } catch (DateTimeParseException e) {
      try {
        LocalDateTime dt = LocalDateTime.parse(jsonDateTime, formatter);
        instant = dt.toInstant(ZoneOffset.UTC);
        return toMSSQLDateFormat(instant);
      } catch (DateTimeParseException ex) {
        // no logging since it may generate too much noise
      }
    }
    return instant == null ? null : instant.toString();
  }

  public static String convertToDateFormatWithZeroTime(String jsonDate) {
    String convertedDate = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, formatter);
      convertedDate = DATE_TIME_FORMAT.format(
          Date.from(date.atStartOfDay().atZone(ZoneId.systemDefault()).toInstant()));
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return convertedDate;
  }

  public static String convertToDateFormat(String jsonDate) {
    String convertedDate = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, formatter);
      convertedDate = DATE_FORMAT.format(
          Date.from(date.atStartOfDay().atZone(ZoneId.systemDefault()).toInstant()));
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return convertedDate;
  }

  public static String convertToGeneralDateFormat(String jsonDate) {
    String convertedDate = null;
    try {
      LocalDate date = LocalDate.parse(jsonDate, formatter);
      convertedDate = date.toString();
    } catch (DateTimeParseException e) {
      // no logging since it may generate too much noise
    }
    return convertedDate;
  }

  private static String toMSSQLDateFormat(Instant instant) {
    String str = MILLISECONDS_PATTERN.matcher(instant.toString().replace('T', ' ').replace("Z", ""))
        .replaceAll("." + (instant.getNano() / 1000000 == 0 ? "0"
            : (instant.getNano() / 1000 + 500) / 1000));
    return (instant.getNano() / 1000000) > 0 ? str : str + ".0";
  }

  private static String toRedshiftDateFormat(Instant instant) {
    return MILLISECONDS_PATTERN.matcher(instant.toString().replace('T', ' ').replace("Z", "+00"))
        .replaceAll("." + instant.getNano() / 1000);
  }

  private static String toBigqueryDenormalizedDateFormat(Instant instant) {
    return MILLISECONDS_PATTERN.matcher(instant.toString().replace("Z", ""))
        .replaceAll("." + (instant.getNano() / 1000000) * 1000);
  }

  private static String toDatabricksDateFormat(Instant instant) {
    return String.format("***\"member0\":%s,\"member1\":null***",MILLISECONDS_PATTERN.matcher(instant.toString().replace('T', ' ').replace("Z", ""))
        .replaceAll("." + (instant.getNano() / 1000000) * 1000));
  }

}
