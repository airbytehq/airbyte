/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import static com.datastax.oss.driver.api.querybuilder.QueryBuilder.now;

import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.BoundStatement;
import com.datastax.oss.driver.api.core.cql.PreparedStatement;
import com.datastax.oss.driver.api.core.metadata.TokenMap;
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

  public void truncate(String keyspace, String tableName) {
    var query = QueryBuilder.truncate(keyspace, tableName).build();
    cqlSession.execute(query);
  }

  public List<CassandraRecord> select(String keyspace, String tableName) {
    var query = QueryBuilder.selectFrom(keyspace, tableName)
        .columns(columnId, columnData, columnTimestamp)
        .build();
    return cqlSession.execute(query)
        .map(result -> new CassandraRecord(
            result.get(columnId, UUID.class),
            result.get(columnData, String.class),
            result.get(columnTimestamp, Instant.class)))
        .all();
  }

  public List<Tuple<String, List<String>>> retrieveMetadata() {
    return cqlSession.getMetadata().getKeyspaces().values().stream()
        .map(keyspace -> Tuple.of(keyspace.getName().toString(), keyspace.getTables().values()
            .stream()
            .map(table -> table.getName().toString())
            .collect(Collectors.toList())))
        .collect(Collectors.toList());
  }

  public void copy(String keyspace, String sourceTable, String destinationTable) {
    var select = String.format("SELECT * FROM %s.%s WHERE token(%s) > ? AND token(%s) <= ?",
        keyspace, sourceTable, columnId, columnId);

    var selectStatement = cqlSession.prepare(select);

    var insert = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)",
        keyspace, destinationTable, columnId, columnData, columnTimestamp);

    var insertStatement = cqlSession.prepare(insert);

    // perform full table scan in parallel using token ranges
    // optimal for copying large amounts of data
    cqlSession.getMetadata().getTokenMap()
        .map(TokenMap::getTokenRanges)
        .orElseThrow(IllegalStateException::new)
        .stream()
        .flatMap(range -> range.unwrap().stream())
        .map(range -> selectStatement.bind(range.getStart(), range.getEnd()))
        // explore datastax 4.x async api as an alternative for async processing
        .map(selectBoundStatement -> executorService.submit(() -> asyncInsert(selectBoundStatement, insertStatement)))
        .forEach(this::awaitThread);

  }

  private void asyncInsert(BoundStatement select, PreparedStatement insert) {
    var boundStatements = cqlSession.execute(select).all().stream()
        .map(r -> CassandraRecord.of(
            r.get(columnId, UUID.class),
            r.get(columnData, String.class),
            r.get(columnTimestamp, Instant.class)))
        .map(r -> insert.bind(r.getId(), r.getData(), r.getTimestamp())).toList();

    boundStatements.forEach(boundStatement -> {
      var resultSetCompletionStage = cqlSession.executeAsync(boundStatement);
      resultSetCompletionStage.whenCompleteAsync((res, err) -> {
        if (err != null) {
          LOGGER.error("Something went wrong during async insertion: " + err.getMessage());
        }
      });
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
    // wait for tasks completion and terminate executor gracefully
    executorService.shutdown();
    // close cassandra session for the given config
    SessionManager.closeSession(cassandraConfig);
  }

}
