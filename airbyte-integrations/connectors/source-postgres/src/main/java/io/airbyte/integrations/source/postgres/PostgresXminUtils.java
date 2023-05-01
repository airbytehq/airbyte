package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresXminUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresXminUtils.class);

  public static boolean isXmin(final JsonNode config) {
    final boolean isXmin = config.hasNonNull("replication_method") && config.get("replication_method").asText().equals("Xmin");
    LOGGER.info("Using Xmin replication: {}", isXmin);
    return isXmin;
  }

  public static AirbyteStream addXminMetadataColumn(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number", "airbyte_type", "integer"));
    properties.set("xmin", numberType);

    return stream;
  }

  public static List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
      final StateManager stateManager,
      final Instant emittedAt,
      final JdbcCompatibleSourceOperations sourceOperations) {

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    /* Process each stream :
       1. If a stream doesn't exist in the source anymore, skip it.
       2. Get the xmin cursor for the stream.
     */
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = airbyteStream.getStream().getName();
      final String namespace = airbyteStream.getStream().getNamespace();

      // Skip syncing the stream if it doesn't exist in the source.
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
          stream.getName());
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }

      // Build the query for this stream. Cursor value, fields to query, etc
      //final int xminCursorValue = -1;

      final TableInfo<CommonField<PostgresType>> table = tableNameToTable
          .get(fullyQualifiedTableName);
      final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(CommonField::getName)
        .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
        .collect(Collectors.toList());

      final AutoCloseableIterator<JsonNode> queryStream =
          queryTableXmin(database, selectedDatabaseFields, table.getNameSpace(),
              table.getName(), sourceOperations);
      iteratorList.add(getMessageIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli()));
      iterator = AutoCloseableIterators.transform(
          autoCloseableIterator -> new XminStateIterator(
              autoCloseableIterator,
              stateManager,
              pair),
          airbyteMessageIterator,
          AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()));
      // Add a state decorator;
      }

    return iteratorList;
  }

  public static AutoCloseableIterator<JsonNode> queryTableXmin(final JdbcDatabase database,
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final JdbcCompatibleSourceOperations sourceOperations) {
    LOGGER.info("Queueing query for table: {}", tableName);
    final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> {
              LOGGER.info("Preparing query for table: {}", tableName);
              final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
                  database.getMetaData().getIdentifierQuoteString());
              /*final String quotedCursorField = enquoteIdentifier(cursorInfo.getCursorField(), getQuoteString());


              final String wrappedColumnNames = getWrappedColumnNames(database, connection, columnNames, schemaName, tableName);*/
              final StringBuilder sql = new StringBuilder(String.format("SELECT * FROM %s",
                  fullTableName));

              final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());
              LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
              return preparedStatement;
            },
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private static AutoCloseableIterator<AirbyteMessage> getMessageIterator(
      final AutoCloseableIterator<JsonNode> recordIterator,
      final String streamName,
      final String namespace,
      final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r)));
  }
}
