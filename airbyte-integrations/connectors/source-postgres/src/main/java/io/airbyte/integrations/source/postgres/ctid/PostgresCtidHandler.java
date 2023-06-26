/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.RowDataWithCtid;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
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
import java.util.Objects;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCtidHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCtidHandler.class);

  private final JsonNode config;
  private final JdbcDatabase database;
  private final CtidPostgresSourceOperations sourceOperations;
  private final String quoteString;
  private final CtidStateManager ctidStateManager;
  private final Map<AirbyteStreamNameNamespacePair, Long> fileNodes;
  final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes;
  private final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;
  private final BiFunction<AirbyteStreamNameNamespacePair, JsonNode, AirbyteStateMessage> finalStateMessageSupplier;
  private static final int QUERY_TARGET_SIZE_GB = 1; // TEMP
  public static final double MEGABYTE = Math.pow(1024, 2);

  public PostgresCtidHandler(final JsonNode config,
                             final JdbcDatabase database,
                             final CtidPostgresSourceOperations sourceOperations,
                             final String quoteString,
                             final Map<AirbyteStreamNameNamespacePair, Long> fileNodes,
                             final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes,
                             final CtidStateManager ctidStateManager,
                             final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier,
                             final BiFunction<AirbyteStreamNameNamespacePair, JsonNode, AirbyteStateMessage> finalStateMessageSupplier) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.fileNodes = fileNodes;
    this.tableBlockSizes = tableBlockSizes;
    this.ctidStateManager = ctidStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.finalStateMessageSupplier = finalStateMessageSupplier;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                             final Instant emmitedAt) {
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
        final TableInfo<CommonField<PostgresType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final List<String> selectedDatabaseFields = table.getFields()
            .stream()
            .map(CommonField::getName)
            .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
            .toList();
        final AutoCloseableIterator<RowDataWithCtid> queryStream = queryTableCtid(
            selectedDatabaseFields,
            table.getNameSpace(),
            table.getName(),
            tableBlockSizes.get(pair).tableSize(),
            tableBlockSizes.get(pair).blockSize());
        final AutoCloseableIterator<AirbyteMessageWithCtid> recordIterator =
            getRecordIterator(queryStream, streamName, namespace, emmitedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, pair);
        final AutoCloseableIterator<AirbyteMessage> logAugmented = augmentWithLogs(recordAndMessageIterator, pair, streamName);
        iteratorList.add(logAugmented);

      }
    }
    return iteratorList;
  }

  class Ctid {
    final long page;
    final long tuple;

     Ctid(final long page, final long tuple) {
      this.page = page;
      this.tuple = tuple;
    }
     Ctid(final String ctid) {
      final Pattern p = Pattern.compile("\\d+");
      final Matcher m = p.matcher(ctid);
      if (m.find()) {
        final String ctidPageStr = m.group();
        this.page = Long.parseLong(ctidPageStr);
      }
      if (m.find()) {
        final String ctidTupleStr = m.group();
        this.tuple = Long.parseLong(ctidTupleStr);
      }
      Objects.requireNonNull(this.page);
      Objects.requireNonNull(this.tuple);
    }
  }
  public static List<Pair<String, String>> ctidQueryBounds(final String startCtid, final long relationSize, final long blockSize, final int chunkSizeGB) {
    final Pattern p = Pattern.compile("\\d+");
    final Matcher m = p.matcher(startCtid);
    m.find();
    String ctidPageStr = m.group();
    Long ctidPage = Long.parseLong(ctidPageStr);
    m.find();
    String ctidTupleStr = m.group();

    final List<Pair<String, String>> chunks = new ArrayList<>();
    long lowerBound = ctidPage;
    long upperBound = 0;
    final double oneGigaPages = MEGABYTE * 1000 / blockSize;
    final long eachStep = (long)oneGigaPages * chunkSizeGB;
    LOGGER.info("Will read {} pages to get {}GB", eachStep, chunkSizeGB);
    final long theoreticalLastPage = relationSize / blockSize;
    LOGGER.info("Theoretical last page {}", theoreticalLastPage);
    upperBound = lowerBound + eachStep;
    chunks.add(Pair.of("(%d,%s)".formatted(lowerBound, ctidTupleStr), "(%d,%d)".formatted(upperBound, 0)));
    while (upperBound < theoreticalLastPage) {
      lowerBound = upperBound;
      upperBound += eachStep;
      chunks.add(Pair.of("(%d,%d)".formatted(lowerBound, 0), upperBound > theoreticalLastPage ? null : "(%d,%d)".formatted(upperBound, 0)));
    }
    return chunks;
  }

  private AutoCloseableIterator<RowDataWithCtid> queryTableCtid(
                                                                final List<String> columnNames,
                                                                final String schemaName,
                                                                final String tableName,
                                                                final long tableSize,
                                                                final long blockSize) {

    LOGGER.info("Queueing query for table: {}", tableName);
    final AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);

    final CtidStatus currentCtidStatus = ctidStateManager.getCtidStatus(airbyteStream);

    final List<Pair<String, String>> chunks = ctidQueryBounds((currentCtidStatus == null) ? "(0,0)" : currentCtidStatus.getCtid(), tableSize, blockSize, QUERY_TARGET_SIZE_GB);
    final List<AutoCloseableIterator<RowDataWithCtid>> its = new ArrayList<>();
    chunks.forEach(p -> {
      its.add(AutoCloseableIterators.lazyIterator(() -> {
        try {
          final Stream<RowDataWithCtid> stream = database.unsafeQuery(
              connection -> createCtidQueryStatement(connection, columnNames, schemaName, tableName, airbyteStream, p.getLeft(), p.getRight()),sourceOperations::recordWithCtid);

          return AutoCloseableIterators.fromStream(stream, airbyteStream);
        } catch (final SQLException e) {
          throw new RuntimeException(e);
        }
      }, airbyteStream));
    });
    return AutoCloseableIterators.concatWithEagerClose(its);
  }

  private PreparedStatement createCtidQueryStatement(
                                                     final Connection connection,
                                                     final List<String> columnNames,
                                                     final String schemaName,
                                                     final String tableName,
                                                     final AirbyteStreamNameNamespacePair airbyteStream,
                                                      final String lowerBound, final String upperBound) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);
      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);
      if (upperBound != null) {
        final String sql = "SELECT ctid, %s FROM %s WHERE ctid > ?::tid AND ctid <= ?::tid".formatted(wrappedColumnNames, fullTableName);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        preparedStatement.setObject(1, lowerBound);
        preparedStatement.setObject(2, upperBound);
        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
        return preparedStatement;
      } else {
        final String sql = "SELECT ctid, %s FROM %s WHERE ctid > ?::tid".formatted(wrappedColumnNames, fullTableName);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        preparedStatement.setObject(1, lowerBound);
        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
        return preparedStatement;
      }
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessageWithCtid> getRecordIterator(
                                                                          final AutoCloseableIterator<RowDataWithCtid> recordIterator,
                                                                          final String streamName,
                                                                          final String namespace,
                                                                          final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessageWithCtid(new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r.data())),
        r.ctid()));
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
          if (count % 1_000_000 == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessageWithCtid> recordIterator,
                                                                 final AirbyteStreamNameNamespacePair pair) {

    final CtidStatus currentCtidStatus = ctidStateManager.getCtidStatus(pair);
    final JsonNode incrementalState =
        (currentCtidStatus == null || currentCtidStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
            : currentCtidStatus.getIncrementalState();
    final Long latestFileNode = fileNodes.get(pair);
    assert latestFileNode != null;

    final Duration syncCheckpointDuration =
        config.get("sync_checkpoint_seconds") != null ? Duration.ofSeconds(config.get("sync_checkpoint_seconds").asLong())
            : CtidStateIterator.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get("sync_checkpoint_records") != null ? config.get("sync_checkpoint_records").asLong()
        : CtidStateIterator.SYNC_CHECKPOINT_RECORDS;

    return AutoCloseableIterators.transformIterator(
        r -> new CtidStateIterator(r, pair, latestFileNode, incrementalState, finalStateMessageSupplier,
            syncCheckpointDuration, syncCheckpointRecords),
        recordIterator, pair);
  }

}
