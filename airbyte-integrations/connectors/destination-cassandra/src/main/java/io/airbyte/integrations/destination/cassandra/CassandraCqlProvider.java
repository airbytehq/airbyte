/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static com.datastax.oss.driver.api.querybuilder.QueryBuilder.now;

import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.BoundStatement;
import com.datastax.oss.driver.api.core.metadata.TokenMap;
import com.datastax.oss.driver.api.core.metadata.schema.KeyspaceMetadata;
import com.datastax.oss.driver.api.core.type.DataTypes;
import com.datastax.oss.driver.api.core.uuid.Uuids;
import com.datastax.oss.driver.api.querybuilder.QueryBuilder;
import com.datastax.oss.driver.api.querybuilder.SchemaBuilder;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.Closeable;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class CassandraCqlProvider implements Closeable {

  private static final Logger LOGGER = LoggerFactory.getLogger(CassandraCqlProvider.class);

  private static final int N_THREADS = Runtime.getRuntime().availableProcessors();

  private final ExecutorService executorService;

  private final CqlSession cqlSession;

  private final CassandraConfig cassandraConfig;

  private final String columnId;

  private final String columnData;

  private final String columnTimestamp;

  public CassandraCqlProvider(CassandraConfig cassandraConfig) {
    this.cassandraConfig = cassandraConfig;
    this.cqlSession = SessionManager.initSession(cassandraConfig);
    var nameTransformer = new CassandraNameTransformer(cassandraConfig);
    this.columnId = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_AB_ID);
    this.columnData = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_DATA);
    this.columnTimestamp = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    this.executorService = Executors.newFixedThreadPool(N_THREADS);
  }

  public void createKeySpaceIfNotExists(String keyspace, int replicationFactor) {
    var query = SchemaBuilder.createKeyspace(keyspace)
        .ifNotExists()
        .withSimpleStrategy(replicationFactor)
        .build();
    cqlSession.execute(query);
  }

  public void createTableIfNotExists(String keyspace, String tableName) {
    var query = SchemaBuilder.createTable(keyspace, tableName)
        .ifNotExists()
        .withPartitionKey(columnId, DataTypes.UUID)
        .withColumn(columnData, DataTypes.TEXT)
        .withColumn(columnTimestamp, DataTypes.TIMESTAMP)
        .build();
    cqlSession.execute(query);
  }

  public void dropTableIfExists(String keyspace, String tableName) {
    var query = SchemaBuilder.dropTable(keyspace, tableName)
        .ifExists()
        .build();
    cqlSession.execute(query);
  }

  public void insert(String keyspace, String tableName, String jsonData) {
    var query = QueryBuilder.insertInto(keyspace, tableName)
        .value(columnId, QueryBuilder.literal(Uuids.random()))
        .value(columnData, QueryBuilder.literal(jsonData))
        .value(columnTimestamp, QueryBuilder.toTimestamp(now()))
        .build();
    cqlSession.execute(query);
  }

  public List<TableRecord> select(String keyspace, String tableName) {
    var query = QueryBuilder.selectFrom(keyspace, tableName)
        .columns(columnId, columnData, columnTimestamp)
        .all()
        .build();
    return cqlSession.execute(query)
        .map(result -> new TableRecord(
            result.get(columnId, UUID.class),
            result.get(columnData, String.class),
            result.get(columnTimestamp, Instant.class)))
        .all();
  }

  public void truncate(String keyspace, String tableName) {
    var query = QueryBuilder.truncate(keyspace, tableName).build();
    cqlSession.execute(query);
  }

  public void copy(String keyspace, String sourceTable, String destinationTable) {
    var metadata = cqlSession.getMetadata();

    var ranges = metadata.getTokenMap()
        .map(TokenMap::getTokenRanges)
        .orElseThrow(IllegalStateException::new);

    // query for retrieving data from different token ranges in parallel
    var pStatement = cqlSession.prepare(
        "SELECT * FROM " + keyspace + "." + sourceTable +
            " WHERE token(" + columnId + ") > ? AND token(" + columnId + ") <= ?");

    // explore datastax 4.x async api as an alternative for async processing
    ranges.stream()
        .map(range -> pStatement.bind(range.getStart(), range.getEnd()))
        .map(bStatement -> executorService.submit(() -> executeQuery(bStatement, keyspace, destinationTable)))
        .forEach(this::awaitThread);

  }

  public List<MetadataTuple> retrieveMetadata() {
    Function<KeyspaceMetadata, MetadataTuple> metaMapper = keyspace -> new MetadataTuple(
        keyspace.getName().toString(),
        keyspace.getTables().values().stream()
            .map(table -> table.getName().toString())
            .collect(Collectors.toList()));

    var metadata = cqlSession.getMetadata();

    return metadata.getKeyspaces().values().stream()
        .map(metaMapper)
        .collect(Collectors.toList());
  }

  private void executeQuery(BoundStatement statement, String keyspace, String destinationTable) {
    var resultSet = cqlSession.execute(statement);
    resultSet.forEach(result -> {
      var query = QueryBuilder.insertInto(keyspace, destinationTable)
          .value(columnId, QueryBuilder.literal(result.get(columnId, UUID.class)))
          .value(columnData, QueryBuilder.literal(result.get(columnData, String.class)))
          .value(columnTimestamp, QueryBuilder.literal(result.get(columnTimestamp, Instant.class)))
          .build();
      cqlSession.execute(query);
    });
  }

  private void awaitThread(Future<?> future) {
    try {
      future.get();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      LOGGER.error("Interrupted thread while copying data with reason: ", e);
    } catch (ExecutionException e) {
      LOGGER.error("Error while copying data with reason: ", e);
    }
  }

  @Override
  public void close() {
    // close cassandra session for the given config
    SessionManager.closeSession(cassandraConfig);
    // wait for tasks completion and terminate executor gracefully
    executorService.shutdown();
  }

}
