/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.SQLException;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Helper class for MySqlSource used to check cdc configuration in case of:
 * <p>
 * 1. adding new source and checking operations #getCheckOperations method.
 * </p>
 * <p>
 * 2. checking whether binlog required from saved cdc offset is available on mysql server
 * #checkBinlog method
 * </p>
 */
public class CdcConfigurationHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcConfigurationHelper.class);
  private static final String CDC_OFFSET = "mysql_cdc_offset";
  private static final String LOG_BIN = "log_bin";
  private static final String BINLOG_FORMAT = "binlog_format";
  private static final String BINLOG_ROW_IMAGE = "binlog_row_image";

  /**
   * Method will check whether required binlog is available on mysql server
   *
   * @param offset - saved cdc offset with required binlog file
   * @param database - database
   */
  public static void checkBinlog(final JsonNode offset, final JdbcDatabase database) {
    final Optional<String> binlogOptional = getBinlog(offset);
    binlogOptional.ifPresent(binlog -> {
      if (isBinlogAvailable(binlog, database)) {
        LOGGER.info("""
                    Binlog %s is available""".formatted(binlog));
      } else {
        final String error =
            """
            Binlog %s is not available. This is a critical error, it means that requested binlog is not present on mysql server. To fix data synchronization you need to reset your data. Please check binlog retention policy configurations."""
                .formatted(binlog);
        LOGGER.error(error);
        throw new RuntimeException("""
                                   Binlog %s is not available.""".formatted(binlog));
      }
    });
  }

  /**
   * Method will get required configurations for cdc sync
   *
   * @return list of List<CheckedConsumer<JdbcDatabase, Exception>>
   */
  public static List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations() {
    return List.of(getCheckOperation(LOG_BIN, "ON"),
        getCheckOperation(BINLOG_FORMAT, "ROW"),
        getCheckOperation(BINLOG_ROW_IMAGE, "FULL"));

  }

  private static boolean isBinlogAvailable(final String binlog, final JdbcDatabase database) {
    if (binlog.isEmpty()) {
      return false;
    }

    try (final Stream<String> binlogs = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SHOW BINARY LOGS"),
        resultSet -> resultSet.getString("Log_name"))) {
      return binlogs.anyMatch(e -> e.equals(binlog));
    } catch (final SQLException e) {
      LOGGER.error("Can not get binlog list. Error: ", e);
      throw new RuntimeException(e);
    }
  }

  private static Optional<String> getBinlog(final JsonNode offset) {
    final JsonNode node = offset.get(CDC_OFFSET);
    final Iterator<Map.Entry<String, JsonNode>> fields = node.fields();
    while (fields.hasNext()) {
      final Map.Entry<String, JsonNode> jsonField = fields.next();
      return Optional.ofNullable(Jsons.deserialize(jsonField.getValue().asText()).path("file").asText());
    }
    return Optional.empty();
  }

  private static CheckedConsumer<JdbcDatabase, Exception> getCheckOperation(final String name, final String value) {
    return database -> {
      final List<String> result = database.queryStrings(
          connection -> connection.createStatement().executeQuery(String.format("show variables where Variable_name = '%s'", name)),
          resultSet -> resultSet.getString("Value"));

      if (result.size() != 1) {
        throw new RuntimeException("Could not query the variable " + name);
      }

      final String resultValue = result.get(0);
      if (!resultValue.equalsIgnoreCase(value)) {
        throw new RuntimeException(String.format("The variable \"%s\" should be set to \"%s\", but it is \"%s\"", name, value, resultValue));
      }
    };
  }

}
