/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;

public class ClickHouseSourceOperations extends JdbcSourceOperations {

  @Override
  public JsonSchemaType getAirbyteType(final JDBCType sourceType) {
    return switch (sourceType) {
      case BIT, BOOLEAN -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      case DATE -> JsonSchemaType.STRING_DATE;
      case TIME -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIME_WITH_TIMEZONE -> JsonSchemaType.STRING_TIME_WITH_TIMEZONE;
      case TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      case TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;
      default -> JsonSchemaType.STRING;
    };
  }

  @Override
  public boolean isCursorType(final JDBCType type) {
    return JdbcUtils.ALLOWED_CURSOR_TYPES.contains(type);
  }

}
