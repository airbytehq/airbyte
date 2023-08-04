package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.mysql.MySqlQueryUtils.TableSizeInfo;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
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
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialLoadHandler {
  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadHandler.class);

  private static final long RECORD_LOGGING_SAMPLE_RATE = 1_000_000;
  private final JsonNode config;
  private final JdbcDatabase database;
  private final MySqlInitialLoadSourceOperations sourceOperations;
  private final String quoteString;
  private final MySqlInitialLoadStateManager initialLoadStateManager;
  private final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap;

  public MySqlInitialLoadHandler(final JsonNode config,
      final JdbcDatabase database,
      final MySqlInitialLoadSourceOperations sourceOperations,
      final String quoteString,
      final MySqlInitialLoadStateManager initialLoadStateManager,
      final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier,
      final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap) {
      final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.tableSizeInfoMap = tableSizeInfoMap;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
      final Instant emittedAt) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {
        // Grab the selected fields to sync
        final TableInfo<CommonField<MysqlType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final List<String> selectedDatabaseFields = table.getFields()
            .stream()
            .map(CommonField::getName)
            .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
            .collect(Collectors.toList());
        final long numRowsToFetchPerQuery = 0;
        final AutoCloseableIterator<JsonNode> queryStream = queryTablePk(selectedDatabaseFields, table.getNameSpace(), table.getName(),
            numRowsToFetchPerQuery);
        final AutoCloseableIterator<AirbyteMessage> recordIterator =
            getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, pair);

        iteratorList.add(augmentWithLogs(recordAndMessageIterator, pair, streamName));

      }
    }
    return iteratorList;
  }

  private long calculateNumRowsToFetchPerQuery(final TableSizeInfo tableSizeInfo) {
    return 0;
  }

  private AutoCloseableIterator<JsonNode> queryTablePk(
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final long numRowsToFetchPerQuery) {
    LOGGER.info("Queueing query for table: {}", tableName);
    final AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final PrimaryKeyLoadStatus pkLoadStatus = initialLoadStateManager.getPrimaryKeyLoadStatus(airbyteStream);
        // Rather than trying to read an entire table with a "WHERE pk > 0" query,
        // We are creating a list of lazy iterators each holding a subquery according to the plan.
        // All subqueries are then composed in a single composite iterator.
        // Because list consists of lazy iterators, the query is only executing when needed one after the other.
        final List<PrimaryKeyLoadStatus> primaryKeyStatuses = getPrimaryKeyStatuses(initialLoadStateManager);
        final PrimaryKeyInfo pkInfo = initialLoadStateManager.getPrimaryKeyInfo(airbyteStream);
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> createPkQueryStatement(connection, columnNames, schemaName, tableName, pkInfo, pkLoadStatus,
                numRowsToFetchPerQuery),
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private List<PrimaryKeyLoadStatus> getPrimaryKeyStatuses(final MySqlInitialLoadStateManager initialLoadStateManager) {
    return null;
  }

  private PreparedStatement createPkQueryStatement(
      final Connection connection,
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final PrimaryKeyInfo pkInfo,
      final PrimaryKeyLoadStatus pkLoadStatus,
      final long numRowsToFetchPerQuery) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);

      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);

      final PreparedStatement preparedStatement =
          getPkPreparedStatement(connection, wrappedColumnNames, fullTableName, pkLoadStatus, pkInfo, numRowsToFetchPerQuery);
      LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
      return preparedStatement;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private PreparedStatement getPkPreparedStatement(final Connection connection,
      final String wrappedColumnNames,
      final String fullTableName,
      final PrimaryKeyLoadStatus pkLoadStatus,
      final PrimaryKeyInfo pkInfo, final long numRowsToFetchPerQuery)
      throws SQLException {

    if (pkLoadStatus == null) {
      final String quotedCursorField = enquoteIdentifier(pkInfo.pkFieldName(), quoteString);
      final String sql = String.format("SELECT %s FROM %s ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
          quotedCursorField, quotedCursorField, numRowsToFetchPerQuery);
      final PreparedStatement preparedStatement = connection.prepareStatement(sql);
      return preparedStatement;

    } else {
      final String quotedCursorField = enquoteIdentifier(pkLoadStatus.getPkName(), quoteString);
      // Since a pk is unique, we can issue a > query instead of a >=, as there cannot be two records with the same pk.
      final String sql = String.format("SELECT %s FROM %s WHERE %s > ? ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
          quotedCursorField, quotedCursorField, numRowsToFetchPerQuery);
      final PreparedStatement preparedStatement = connection.prepareStatement(sql);
      final MysqlType cursorFieldType = pkInfo.fieldType();
      sourceOperations.setCursorField(preparedStatement, 1, cursorFieldType, pkLoadStatus.getPkVal());

      return preparedStatement;
    }
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessage> getRecordIterator(
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
      final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair,
      final String streamName) {
    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()),
        r -> {
          final long count = recordCount.incrementAndGet();
          if (count % RECORD_LOGGING_SAMPLE_RATE == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessage> recordIterator,
      final AirbyteStreamNameNamespacePair pair) {

    final PrimaryKeyLoadStatus currentPkLoadStatus = initialLoadStateManager.getPrimaryKeyLoadStatus(pair);
    final JsonNode incrementalState =
        (currentPkLoadStatus == null || currentPkLoadStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
            : currentPkLoadStatus.getIncrementalState();

    final Duration syncCheckpointDuration =
        config.get("sync_checkpoint_seconds") != null ? Duration.ofSeconds(config.get("sync_checkpoint_seconds").asLong())
            : MySqlInitialSyncStateIterator.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get("sync_checkpoint_records") != null ? config.get("sync_checkpoint_records").asLong()
        : MySqlInitialSyncStateIterator.SYNC_CHECKPOINT_RECORDS;

    return AutoCloseableIterators.transformIterator(
        r -> new MySqlInitialSyncStateIterator(r, pair, initialLoadStateManager, incrementalState,
            syncCheckpointDuration, syncCheckpointRecords),
        recordIterator, pair);
  }
}
