package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MagicSyncHandler {

  private final JdbcCompatibleSourceOperations sourceOperations;
  private final JdbcDatabase database;
  private final String quoteString;
  private final MagicSyncStateManager magicSyncStateManager;

  private static final Logger LOGGER = LoggerFactory.getLogger(MagicSyncHandler.class);

  public MagicSyncHandler(final JdbcDatabase database,
      final JdbcCompatibleSourceOperations sourceOperations,
      final String quoteString,
      final MagicSyncStateManager magicSyncStateManager) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.magicSyncStateManager = magicSyncStateManager;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
      final Instant emittedAt) {

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    /*
     */
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = airbyteStream.getStream().getName();
      final String namespace = airbyteStream.getStream().getNamespace();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName,
          namespace);

      // Skip syncing the stream if it doesn't exist in the source.
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
          stream.getName());
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }

      // Grab the selected fields to sync
      final TableInfo<CommonField<PostgresType>> table = tableNameToTable
          .get(fullyQualifiedTableName);
      final List<String> selectedDatabaseFields = table.getFields()
          .stream()
          .map(CommonField::getName)
          .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
          .collect(Collectors.toList());

      final AutoCloseableIterator<JsonNode> queryStream = queryTableMagicSync(selectedDatabaseFields, table.getNameSpace(), table.getName());
      final AutoCloseableIterator<AirbyteMessage> recordIterator =
          getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
      final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, pair);

      iteratorList.add(augmentWithLogs(recordAndMessageIterator, pair, streamName));
    }

    return iteratorList;
  }

  private AutoCloseableIterator<JsonNode> queryTableMagicSync(
      final List<String> columnNames,
      final String schemaName,
      final String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    final AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> createMagicSyncQueryStatement(connection, columnNames, schemaName, tableName, airbyteStream),
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private PreparedStatement createMagicSyncQueryStatement(
      final Connection connection,
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final AirbyteStreamNameNamespacePair airbyteStream) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);

      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);
      final StringBuilder sql = new StringBuilder(String.format("SELECT *, md5(pk::text) as key_hash, md5(table_pk::text) as val_hash FROM %s", fullTableName));

      final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());

      LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
      return preparedStatement;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private static AutoCloseableIterator<AirbyteMessage> getRecordIterator(
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

  // Augments the given iterator with record count logs.
  private AutoCloseableIterator<AirbyteMessage> augmentWithLogs(final AutoCloseableIterator<AirbyteMessage> iterator,
      final AirbyteStreamNameNamespacePair pair, final String streamName) {
    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()),
        r -> {
          final long count = recordCount.incrementAndGet();
          if (count % 10000 == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessage> recordIterator,
      final AirbyteStreamNameNamespacePair pair) {
    return  AutoCloseableIterators.transform(
        autoCloseableIterator -> new MagicSyncStateIterator(
            autoCloseableIterator,
            pair,
            magicSyncStateManager.getInvertibleBloomFilter(pair)),
        recordIterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()));
  }
}
