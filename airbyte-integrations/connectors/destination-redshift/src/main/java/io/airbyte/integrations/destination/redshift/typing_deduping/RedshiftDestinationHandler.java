/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.jooq.SQLDialect;

@Slf4j
public class RedshiftDestinationHandler extends JdbcDestinationHandler<RedshiftState> {

  public RedshiftDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase, String rawNamespace) {
    // :shrug: apparently this works better than using POSTGRES
    super(databaseName, jdbcDatabase, rawNamespace, SQLDialect.DEFAULT);
  }

  @Override
  public void execute(final Sql sql) throws Exception {
    final List<List<String>> transactions = sql.transactions();
    final UUID queryId = UUID.randomUUID();
    for (final List<String> transaction : transactions) {
      final UUID transactionId = UUID.randomUUID();
      log.info("Executing sql {}-{}: {}", queryId, transactionId, String.join("\n", transaction));
      final long startTime = System.currentTimeMillis();

      try {
        // Original list is immutable, so copying it into a different list.
        final List<String> modifiedStatements = new ArrayList<>();
        // This is required for Redshift to retrieve Json path query with upper case characters, even after
        // specifying quotes.
        // see https://github.com/airbytehq/airbyte/issues/33900
        modifiedStatements.add("SET enable_case_sensitive_identifier to TRUE;\n");
        modifiedStatements.addAll(transaction);
        getJdbcDatabase().executeWithinTransaction(modifiedStatements);
      } catch (final SQLException e) {
        log.error("Sql {}-{} failed", queryId, transactionId, e);
        // This is a big hammer for something that should be much more targetted, only when executing the
        // DROP TABLE command.
        if (e.getMessage().contains("ERROR: cannot drop table") && e.getMessage().contains("because other objects depend on it")) {
          throw new ConfigErrorException(
              "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter", e);
        }
        throw e;
      }

      log.info("Sql {}-{} completed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
    }
  }

  @Override
  protected String toJdbcTypeName(AirbyteType airbyteType) {
    // This is mostly identical to the postgres implementation, but swaps jsonb to super
    if (airbyteType instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toJdbcTypeName(airbyteProtocolType);
    }
    return switch (airbyteType.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE, Array.TYPE -> "super";
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> toJdbcTypeName(((Union) airbyteType).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + airbyteType);
    };
  }

  @Override
  protected RedshiftState toDestinationState(JsonNode json) {
    return new RedshiftState(
        json.hasNonNull("needsSoftReset") && json.get("needsSoftReset").asBoolean(),
        json.hasNonNull("isAirbyteMetaPresentInRaw") && json.get("isAirbyteMetaPresentInRaw").asBoolean());
  }

  private String toJdbcTypeName(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case STRING -> "varchar";
      case NUMBER -> "numeric";
      case INTEGER -> "int8";
      case BOOLEAN -> "bool";
      case TIMESTAMP_WITH_TIMEZONE -> "timestamptz";
      case TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp";
      case TIME_WITH_TIMEZONE -> "timetz";
      case TIME_WITHOUT_TIMEZONE -> "time";
      case DATE -> "date";
      case UNKNOWN -> "super";
    };
  }

  // Do not use SVV_TABLE_INFO to get isFinalTableEmpty.
  // See https://github.com/airbytehq/airbyte/issues/34357

}
