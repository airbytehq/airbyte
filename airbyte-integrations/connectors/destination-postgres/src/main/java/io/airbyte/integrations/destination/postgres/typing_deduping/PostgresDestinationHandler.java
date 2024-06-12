/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import org.jooq.SQLDialect;

public class PostgresDestinationHandler extends JdbcDestinationHandler<PostgresState> {

  public PostgresDestinationHandler(String databaseName, JdbcDatabase jdbcDatabase, String rawTableSchema) {
    super(databaseName, jdbcDatabase, rawTableSchema, SQLDialect.POSTGRES);
  }

  @Override
  protected String toJdbcTypeName(AirbyteType airbyteType) {
    // This is mostly identical to the postgres implementation, but swaps jsonb to super
    if (airbyteType instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toJdbcTypeName(airbyteProtocolType);
    }
    return switch (airbyteType.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE, Array.TYPE -> "jsonb";
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> toJdbcTypeName(((Union) airbyteType).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + airbyteType);
    };
  }

  @Override
  protected PostgresState toDestinationState(JsonNode json) {
    return new PostgresState(
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
      case UNKNOWN -> "jsonb";
    };
  }

}
