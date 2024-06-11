/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.BIGINT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.BIGINT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DATE;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DATETIME;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DECIMAL;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DECIMAL_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DOUBLE;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.DOUBLE_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.FLOAT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.FLOAT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.INT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.INT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.LONGTEXT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.MEDIUMINT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.MEDIUMINT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.MEDIUMTEXT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.SMALLINT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.SMALLINT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TEXT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TIME;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TIMESTAMP;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TINYINT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TINYINT_UNSIGNED;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.TINYTEXT;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.VARCHAR;
import static io.airbyte.integrations.source.singlestore.SingleStoreType.YEAR;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.singlestore.jdbc.client.result.ResultSetMetaData;
import io.airbyte.cdk.db.SourceOperations;
import io.airbyte.cdk.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcConstants;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Set;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreSourceOperations extends AbstractJdbcCompatibleSourceOperations<SingleStoreType> implements
    SourceOperations<ResultSet, SingleStoreType> {

  private static final Set<SingleStoreType> ALLOWED_CURSOR_TYPES = Set.of(TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT,
      MEDIUMINT_UNSIGNED, INT, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED, FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED, DECIMAL, DECIMAL_UNSIGNED, DATE,
      DATETIME, TIMESTAMP, TIME, YEAR, VARCHAR, TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT);

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreSourceOperations.class);

  @Override
  public void copyToJsonField(@NotNull ResultSet resultSet, int colIndex, @NotNull ObjectNode json) throws SQLException {
    final ResultSetMetaData metaData = (ResultSetMetaData) resultSet.getMetaData();
    String type = metaData.getColumnTypeName(colIndex);
    final String columnName = metaData.getColumnName(colIndex);
    SingleStoreType columnType = SingleStoreType.getByName(type);

    switch (columnType) {
      case BIT, TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY -> putBinary(json, columnName, resultSet, colIndex);
      case TINYINT, TINYINT_UNSIGNED, YEAR -> putShortInt(json, columnName, resultSet, colIndex);
      case SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED, INT -> putInteger(json, columnName, resultSet, colIndex);
      case INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED -> putBigInt(json, columnName, resultSet, colIndex);
      case FLOAT, FLOAT_UNSIGNED -> putFloat(json, columnName, resultSet, colIndex);
      case DOUBLE, DOUBLE_UNSIGNED -> putDouble(json, columnName, resultSet, colIndex);
      case DECIMAL, DECIMAL_UNSIGNED -> putBigDecimal(json, columnName, resultSet, colIndex);
      case DATE -> putDate(json, columnName, resultSet, colIndex);
      case DATETIME, TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
      case TIME, CHAR, VARCHAR, TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT, JSON, ENUM, SET -> putString(json, columnName, resultSet, colIndex);
      case NULL -> json.set(columnName, NullNode.instance);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }

  @Override
  public void setCursorField(@NotNull PreparedStatement preparedStatement,
                             int parameterIndex,
                             final SingleStoreType cursorFieldType,
                             @NotNull String value)
      throws SQLException {
    if (cursorFieldType == null) {
      throw new IllegalArgumentException("NULL cannot be used as a cursor.");
    }
    switch (cursorFieldType) {
      case BIT -> setBit(preparedStatement, parameterIndex, value);
      case YEAR, TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED -> setInteger(preparedStatement,
          parameterIndex, value);
      case INT, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED -> setBigInteger(preparedStatement, parameterIndex, value);
      case FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED -> setDouble(preparedStatement, parameterIndex, value);
      case DECIMAL, DECIMAL_UNSIGNED -> setDecimal(preparedStatement, parameterIndex, value);
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case DATETIME, TIMESTAMP -> setTimestamp(preparedStatement, parameterIndex, value);
      case TIME, VARCHAR, TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT -> setString(preparedStatement, parameterIndex, value);
      case TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY -> setBinary(preparedStatement, parameterIndex, value);
      default -> throw new IllegalArgumentException(String.format("%s cannot be used as a cursor.", cursorFieldType));
    }
  }

  @Override
  public SingleStoreType getDatabaseFieldType(@NotNull JsonNode field) {
    try {
      return SingleStoreType.getByName(field.get(INTERNAL_COLUMN_TYPE_NAME).asText());
    } catch (IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(JdbcConstants.INTERNAL_COLUMN_NAME), field.get(JdbcConstants.INTERNAL_SCHEMA_NAME), field.get(JdbcConstants.INTERNAL_TABLE_NAME),
          field.get(JdbcConstants.INTERNAL_COLUMN_TYPE)));
      return SingleStoreType.VARCHAR;
    }
  }

  @Override
  public boolean isCursorType(@Nullable SingleStoreType singlestoreType) {
    return ALLOWED_CURSOR_TYPES.contains(singlestoreType);
  }

  @NotNull
  @Override
  public JsonSchemaType getAirbyteType(SingleStoreType singlestoreType) {
    return switch (singlestoreType) {
      case TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED, INT, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED -> JsonSchemaType.INTEGER;
      case FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED, DECIMAL, DECIMAL_UNSIGNED -> JsonSchemaType.NUMBER;
      case BIT, TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY -> JsonSchemaType.STRING_BASE_64;
      case DATETIME, TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      case DATE -> JsonSchemaType.STRING_DATE;
      case NULL -> JsonSchemaType.NULL;
      default -> JsonSchemaType.STRING;
    };
  }

}
