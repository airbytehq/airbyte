/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static java.sql.JDBCType.BIGINT;
import static java.sql.JDBCType.CHAR;
import static java.sql.JDBCType.DATE;
import static java.sql.JDBCType.DECIMAL;
import static java.sql.JDBCType.DOUBLE;
import static java.sql.JDBCType.FLOAT;
import static java.sql.JDBCType.INTEGER;
import static java.sql.JDBCType.LONGVARCHAR;
import static java.sql.JDBCType.NCHAR;
import static java.sql.JDBCType.NUMERIC;
import static java.sql.JDBCType.NVARCHAR;
import static java.sql.JDBCType.REAL;
import static java.sql.JDBCType.SMALLINT;
import static java.sql.JDBCType.TIME;
import static java.sql.JDBCType.TIMESTAMP;
import static java.sql.JDBCType.TIMESTAMP_WITH_TIMEZONE;
import static java.sql.JDBCType.TIME_WITH_TIMEZONE;
import static java.sql.JDBCType.TINYINT;
import static java.sql.JDBCType.VARCHAR;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Duration;
import java.sql.JDBCType;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresUtils {

  public static final Set<JDBCType> ALLOWED_CURSOR_TYPES = Set.of(TIMESTAMP, TIMESTAMP_WITH_TIMEZONE, TIME, TIME_WITH_TIMEZONE,
      DATE, TINYINT, SMALLINT, INTEGER, BIGINT, FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL,
      CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR);

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresUtils.class);

  private static final String PGOUTPUT_PLUGIN = "pgoutput";

  public static final Duration MAX_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(20);
  public static final Duration DEFAULT_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(5);

  public static String getPluginValue(final JsonNode field) {
    return field.has("plugin") ? field.get("plugin").asText() : PGOUTPUT_PLUGIN;
  }

  public static boolean isCdc(final JsonNode config) {
    final boolean isCdc = config.hasNonNull("replication_method")
        && config.get("replication_method").hasNonNull("replication_slot")
        && config.get("replication_method").hasNonNull("publication");
    LOGGER.info("using CDC: {}", isCdc);
    return isCdc;
  }

  public static Duration getFirstRecordWaitTime(final JsonNode config) {
    if (config.has("initial_waiting_seconds")) {
      final int seconds = config.get("initial_waiting_seconds").asInt();
      if (seconds > MAX_FIRST_RECORD_WAIT_TIME.getSeconds()) {
        LOGGER.warn("First record waiting time is overridden to {} minutes, which is the max time allowed for safety.",
            MAX_FIRST_RECORD_WAIT_TIME.toMinutes());
        return MAX_FIRST_RECORD_WAIT_TIME;
      }

      return Duration.ofSeconds(seconds);
    }

    return DEFAULT_FIRST_RECORD_WAIT_TIME;
  }

}
