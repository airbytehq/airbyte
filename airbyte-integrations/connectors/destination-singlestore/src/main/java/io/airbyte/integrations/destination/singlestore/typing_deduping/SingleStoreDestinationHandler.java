/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.typing_deduping;

import static java.util.Collections.emptyMap;
import static org.jooq.impl.DSL.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.commons.exceptions.SQLRuntimeException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.Condition;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreDestinationHandler extends JdbcDestinationHandler<MinimumDestinationState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreDestinationHandler.class);

  private static final String STATE_TABLE_NAME = "_airbyte_destination_state";
  private static final String STATE_TABLE_COLUMN_NAME = "name";
  private static final String STATE_TABLE_COLUMN_NAMESPACE = "namespace";
  private static final String STATE_TABLE_COLUMN_STATE = "destination_state";
  private static final String STATE_TABLE_COLUMN_UPDATED_AT = "updated_at";

  public SingleStoreDestinationHandler(@NotNull String databaseName, @NotNull JdbcDatabase jdbcDatabase, @NotNull String rawTableSchemaName) {
    super(databaseName, jdbcDatabase, rawTableSchemaName, SQLDialect.MYSQL);
  }

  @NotNull
  @Override
  protected Optional<TableDefinition> findExistingTable(@NotNull StreamId id) throws Exception {
    final var databaseName = id.getFinalNamespace();
    final var tableName = id.getFinalName();
    var retrievedColumnDefns = getJdbcDatabase().executeMetadataQuery(dbMetadata -> {
      var columnDefinitions = new LinkedHashMap<String, ColumnDefinition>();
      LOGGER.info("Retrieving existing columns for {}.{}", databaseName, tableName);
      try {
        ResultSet rs = dbMetadata.getColumns(databaseName, null, tableName, null);
        while (rs.next()) {
          var columnName = rs.getString("COLUMN_NAME");
          var typeName = rs.getString("TYPE_NAME");
          var columnSize = rs.getInt("COLUMN_SIZE");
          var isNullable = rs.getString("IS_NULLABLE");
          columnDefinitions.put(columnName, new ColumnDefinition(
              columnName,
              typeName,
              columnSize,
              "YES".equalsIgnoreCase(isNullable)));
        }
      } catch (SQLException e) {
        LOGGER.error(
            "Failed to retrieve column info for {}.{}",
            databaseName,
            tableName,
            e);
        throw new SQLRuntimeException(e);
      }
      return columnDefinitions;
    });
    if (retrievedColumnDefns.isEmpty()) {
      return Optional.empty();
    }
    return Optional.of(new TableDefinition(retrievedColumnDefns));
  }

  @NotNull
  @Override
  protected ResultSet getTableFromMetadata(@NotNull DatabaseMetaData dbmetadata, @NotNull StreamId id) {
    try {
      return dbmetadata.getTables(id.getRawNamespace(), null, id.getRawName(), null);
    } catch (SQLException e) {
      LOGGER.warn("Failed get raw table metadata", e);
      throw new RuntimeException(e);
    }
  }

  @Override
  @NotNull
  protected Map<AirbyteStreamNameNamespacePair, MinimumDestinationState> getAllDestinationStates() {
    try {
      var createStatement = getDslContext().createTableIfNotExists(quotedName(getRawTableNamespace(), STATE_TABLE_NAME))
          .column(quotedName(STATE_TABLE_COLUMN_NAME), SQLDataType.VARCHAR(256))
          .column(quotedName(STATE_TABLE_COLUMN_NAMESPACE), SQLDataType.VARCHAR(256))
          .column(quotedName(STATE_TABLE_COLUMN_STATE), SQLDataType.VARCHAR(256))
          .column(quotedName(STATE_TABLE_COLUMN_UPDATED_AT), SQLDataType.TIMESTAMP(6)).getSQL(ParamType.INLINED);
      var selectStatement = getDslContext().select(field(quotedName(STATE_TABLE_COLUMN_NAME)),
          field(quotedName(STATE_TABLE_COLUMN_NAMESPACE)),
          field(quotedName(STATE_TABLE_COLUMN_STATE)),
          field(quotedName(STATE_TABLE_COLUMN_UPDATED_AT)))
          .from(quotedName(getRawTableNamespace(), STATE_TABLE_NAME)).orderBy(field(quotedName(STATE_TABLE_COLUMN_UPDATED_AT))).getSQL();
      getJdbcDatabase().execute(createStatement);
      return getJdbcDatabase().queryJsons(selectStatement).stream()
          .map(n -> {
            var record = (ObjectNode) n;
            Map<String, JsonNode> newFields = new HashMap<>();
            var it = record.fieldNames();
            while (it.hasNext()) {
              var fieldName = it.next();
              newFields.put(fieldName.toLowerCase(Locale.getDefault()), record.get(fieldName));
            }
            record.setAll(newFields);
            return record;
          })
          .collect(Collectors.toMap(
              n -> new AirbyteStreamNameNamespacePair(n.get(STATE_TABLE_COLUMN_NAME).asText(), n.get(STATE_TABLE_COLUMN_NAMESPACE).asText()), n -> {
                var stateTextNode = n.get(STATE_TABLE_COLUMN_STATE);
                var stateNode = stateTextNode != null ? Jsons.deserialize(stateTextNode.asText()) : Jsons.emptyObject();
                return toDestinationState(stateNode);
              }));
    } catch (Exception e) {
      LOGGER.warn("Failed to retrieve destination states", e);
      return emptyMap();
    }
  }

  @Override
  public void commitDestinationStates(@NotNull Map<StreamId, ? extends MinimumDestinationState> destinationStates) throws Exception {
    if (destinationStates.isEmpty()) {
      return;
    }
    try {
      var deleteStates = getDslContext().deleteFrom(table(quotedName(getRawTableNamespace(), STATE_TABLE_NAME)))
          .where(destinationStates.keySet().stream()
              .map(streamId -> field(quotedName(STATE_TABLE_COLUMN_NAME)).eq(streamId.getOriginalName())
                  .and(field(quotedName(STATE_TABLE_COLUMN_NAMESPACE)).eq(streamId.getFinalNamespace())))
              .reduce(DSL.falseCondition(), Condition::or))
          .getSQL(ParamType.INLINED);
      var insertStatesStep = getDslContext().insertInto(table(quotedName(getRawTableNamespace(), STATE_TABLE_NAME)))
          .columns(field(quotedName(STATE_TABLE_COLUMN_NAME), String.class),
              field(quotedName(STATE_TABLE_COLUMN_NAMESPACE), String.class),
              field(quotedName(STATE_TABLE_COLUMN_STATE), String.class),
              field(quotedName(STATE_TABLE_COLUMN_UPDATED_AT), String.class));
      for (var entry : destinationStates.entrySet()) {
        var streamId = entry.getKey();
        var value = entry.getValue();
        var stateJson = Jsons.serialize(value);
        insertStatesStep = insertStatesStep
            .values(streamId.getOriginalName(),
                streamId.getOriginalNamespace(),
                stateJson,
                OffsetDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS")));
      }
      var insertStates = insertStatesStep.getSQL(ParamType.INLINED);
      getJdbcDatabase().executeWithinTransaction(List.of(deleteStates, insertStates));
    } catch (Exception e) {
      LOGGER.warn("Failed to commit destination states", e);
    }
  }

  @NotNull
  @Override
  protected String toJdbcTypeName(@Nullable AirbyteType airbyteType) {
    if (airbyteType instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toJdbcTypeName(airbyteProtocolType);
    }
    return switch (airbyteType.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE, Array.TYPE -> "json";
      case Union.TYPE -> toJdbcTypeName(((Union) airbyteType).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + airbyteType);
    };
  }

  @Override
  protected MinimumDestinationState toDestinationState(@Nullable JsonNode json) {
    return new MinimumDestinationState.Impl(json.hasNonNull("needsSoftReset") && json.get("needsSoftReset").asBoolean());
  }

  private String toJdbcTypeName(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case STRING -> "varchar";
      case NUMBER -> "decimal";
      case INTEGER -> "bigint";
      case BOOLEAN -> "bit";
      case TIMESTAMP_WITH_TIMEZONE, TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp";
      case TIME_WITH_TIMEZONE, TIME_WITHOUT_TIMEZONE -> "time";
      case DATE -> "date";
      case UNKNOWN -> "json";
    };
  }

  @Override
  public void createNamespaces(@NotNull Set<String> databases) {
    databases.forEach(d -> {
      try {
        getJdbcDatabase().execute(getDslContext().createDatabaseIfNotExists(d).getSQL());
      } catch (SQLException e) {
        LOGGER.warn("Failed to create destination database", e);
        throw new RuntimeException(e);
      }
    });
  }

}
