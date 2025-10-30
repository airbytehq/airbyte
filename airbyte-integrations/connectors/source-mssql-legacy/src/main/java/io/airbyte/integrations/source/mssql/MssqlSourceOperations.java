/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.sql.ResultSetMetaData;

import io.airbyte.cdk.db.jdbc.AirbyteRecordData;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.integrations.source.mssql.initialsync.CdcMetadataInjector;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Base64;
import java.util.Optional;
import microsoft.sql.DateTimeOffset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSourceOperations.class);

  private final Optional<CdcMetadataInjector> metadataInjector;

  public MssqlSourceOperations() {
    super();
    this.metadataInjector = Optional.empty();
  }

  public MssqlSourceOperations(final Optional<CdcMetadataInjector> metadataInjector) {
    super();
    this.metadataInjector = metadataInjector;
  }

  @Override
  public AirbyteRecordData convertDatabaseRowToAirbyteRecordData(final ResultSet queryContext) throws SQLException {
    final AirbyteRecordData recordData = super.convertDatabaseRowToAirbyteRecordData(queryContext);
    final ObjectNode jsonNode = (ObjectNode) recordData.rawRowData();
    if (!metadataInjector.isPresent()) {
      return recordData;
    }
    metadataInjector.get().inject(jsonNode);
    return new AirbyteRecordData(jsonNode, recordData.meta());
  }

  /**
   * The method is used to set json value by type. Need to be overridden as MSSQL has some its own
   * specific types (ex. Geometry, Geography, Hierarchyid, etc)
   *
   * @throws SQLException
   */
  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json)
      throws SQLException {
    final ResultSetMetaData metadata = (ResultSetMetaData) resultSet
        .getMetaData();
    final String columnName = metadata.getColumnName(colIndex);
    final String columnTypeName = metadata.getColumnTypeName(colIndex);

    // Attempt to access the column. this allows us to know if it is null before we do
    // type-specific parsing. If the column is null, we will populate the null value and skip attempting
    // to
    // parse the column value.
    resultSet.getObject(colIndex);
    if (resultSet.wasNull()) {
      json.putNull(columnName);
    } else if (columnTypeName.equalsIgnoreCase("time")) {
      putTime(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equalsIgnoreCase("datetimeoffset")) {
      // JDBC will recognize such columns as VARCHAR. Thus we have to have special handling on it.
      putTimestampWithTimezone(json, columnName, resultSet, colIndex);
    } else {
      super.copyToJsonField(resultSet, colIndex, json);
    }
  }

  @Override
  public JDBCType getDatabaseFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText();
      if (typeName.equalsIgnoreCase("geography")
          || typeName.equalsIgnoreCase("geometry")
          || typeName.equalsIgnoreCase("hierarchyid")) {
        return JDBCType.VARCHAR;
      }

      if (typeName.equalsIgnoreCase("datetime")) {
        return JDBCType.TIMESTAMP;
      }

      if (typeName.equalsIgnoreCase("datetimeoffset")) {
        return JDBCType.TIMESTAMP_WITH_TIMEZONE;
      }

      if (typeName.equalsIgnoreCase("real")) {
        return JDBCType.REAL;
      }

      return JDBCType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt());
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE)));
      return JDBCType.VARCHAR;
    }
  }

  @Override
  protected void putBinary(final ObjectNode node,
                           final String columnName,
                           final ResultSet resultSet,
                           final int index)
      throws SQLException {
    final byte[] bytes = resultSet.getBytes(index);
    final String value = Base64.getEncoder().encodeToString(bytes);
    node.put(columnName, value);
  }

  // @Override
  // protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
  //   final DateTimeFormatter microsecondsFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss[.][SSSSSS]");
  //   node.put(columnName, getObject(resultSet, index, LocalDateTime.class).format(microsecondsFormatter));
  // }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final DateTimeFormatter microsecondsFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss[.][SSSSSS]");
    
    try {
        // Try the original approach
        node.put(columnName, getObject(resultSet, index, LocalDateTime.class).format(microsecondsFormatter));
    } catch (AbstractMethodError | SQLException e) {
        // Fallback for jTDS compatibility
        try {
            // Use jTDS-compatible approach
            Timestamp timestamp = resultSet.getTimestamp(index);
            if (timestamp != null) {
                LocalDateTime localDateTime = timestamp.toLocalDateTime();
                node.put(columnName, localDateTime.format(microsecondsFormatter));
            } else {
                node.putNull(columnName);
            }
        } catch (SQLException ex) {
            // Final fallback - get as string and try to parse
            String timestampStr = resultSet.getString(index);
            if (timestampStr != null && !timestampStr.trim().isEmpty()) {
                try {
                    // Try to parse the string as a timestamp
                    LocalDateTime localDateTime = LocalDateTime.parse(timestampStr.replace(" ", "T"));
                    node.put(columnName, localDateTime.format(microsecondsFormatter));
                } catch (Exception parseEx) {
                    // If all else fails, store as string
                    node.put(columnName, timestampStr);
                }
            } else {
                node.putNull(columnName);
            }
        }
    }
}

  @Override
  public JsonSchemaType getAirbyteType(final JDBCType jdbcType) {
    return switch (jdbcType) {
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case DOUBLE, DECIMAL, FLOAT, NUMERIC, REAL -> JsonSchemaType.NUMBER;
      case BOOLEAN, BIT -> JsonSchemaType.BOOLEAN;
      case NULL -> JsonSchemaType.NULL;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case TIME -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;
      case TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      case DATE -> JsonSchemaType.STRING_DATE;
      default -> JsonSchemaType.STRING;
    };
  }

  @Override
  protected void setTimestampWithTimezone(final PreparedStatement preparedStatement, final int parameterIndex, final String value)
      throws SQLException {
    try {
      final OffsetDateTime offsetDateTime = OffsetDateTime.parse(value, TIMESTAMPTZ_FORMATTER);
      final Timestamp timestamp = Timestamp.valueOf(offsetDateTime.atZoneSameInstant(offsetDateTime.getOffset()).toLocalDateTime());
      // Final step of conversion from
      // OffsetDateTime (a Java construct) object -> Timestamp (a Java construct) ->
      // DateTimeOffset (a Microsoft.sql specific construct)
      // and provide the offset in minutes to the converter
      final DateTimeOffset datetimeoffset = DateTimeOffset.valueOf(timestamp, offsetDateTime.getOffset().getTotalSeconds() / 60);
      preparedStatement.setObject(parameterIndex, datetimeoffset);
    } catch (final DateTimeParseException e) {
      throw new RuntimeException(e);
    }
  }

}
