/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.datastax.driver.core.AbstractTableMetadata;
import com.datastax.driver.core.BatchStatement;
import com.datastax.driver.core.BoundStatement;
import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.DataType;
import com.datastax.driver.core.PreparedStatement;
import com.datastax.driver.core.Session;
import com.datastax.driver.core.querybuilder.QueryBuilder;
import com.datastax.driver.core.schemabuilder.SchemaBuilder;
import com.datastax.driver.core.utils.UUIDs;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.Closeable;
import java.time.Instant;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ScyllaCqlProvider implements Closeable {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScyllaCqlProvider.class);

  private static final int N_THREADS = Runtime.getRuntime().availableProcessors();

  private final ScyllaConfig scyllaConfig;

  private final Cluster cluster;

  private final Session session;

  private final ExecutorService executorService;

  private final String columnId;

  private final String columnData;

  private final String columnTimestamp;

  public ScyllaCqlProvider(ScyllaConfig scyllaConfig) {
    this.scyllaConfig = scyllaConfig;
    var sessionTuple = ScyllaSessionPool.initSession(scyllaConfig);
    this.cluster = sessionTuple.value1();
    this.session = sessionTuple.value2();
    this.executorService = Executors.newFixedThreadPool(N_THREADS);
    var nameTransformer = new ScyllaNameTransformer(scyllaConfig);
    this.columnId = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_AB_ID);
    this.columnData = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_DATA);
    this.columnTimestamp = nameTransformer.outputColumn(JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  public void createKeyspaceIfNotExists(String keyspace) {
    var createKeyspace = SchemaBuilder.createKeyspace(keyspace)
        .ifNotExists()
        .with()
        .replication(Map.of(
            "class", "SimpleStrategy",
            "replication_factor", scyllaConfig.getReplication()))
        .durableWrites(true);
    session.execute(createKeyspace);
  }

  public void createTableIfNotExists(String keyspace, String table) {
    var createTable = SchemaBuilder.createTable(keyspace, table)
        .ifNotExists()
        .addPartitionKey(columnId, DataType.uuid())
        .addColumn(columnData, DataType.text())
        .addColumn(columnTimestamp, DataType.timestamp());
    session.execute(createTable);
  }

  public void dropTableIfExists(String keyspace, String table) {
    var drop = SchemaBuilder.dropTable(keyspace, table).ifExists();
    session.execute(drop);
  }

  public void truncate(String keyspace, String table) {
    var truncate = QueryBuilder.truncate(keyspace, table);
    session.execute(truncate);
  }

  public void insert(String keyspace, String table, String data) {
    var insert = QueryBuilder.insertInto(keyspace, table)
        .value(columnId, UUIDs.random())
        .value(columnData, data)
        .value(columnTimestamp, Instant.now().toEpochMilli());
    session.execute(insert);
  }

  public List<Triplet<UUID, String, Instant>> select(String keyspace, String table) {
    var select = QueryBuilder.select().all().from(keyspace, table);
    return session.execute(select).all().stream()
        .map(r -> Triplet.of(
            r.get(columnId, UUID.class),
            r.get(columnData, String.class),
            r.get(columnTimestamp, Date.class).toInstant()))
        .collect(Collectors.toList());
  }

  public List<Tuple<String, List<String>>> metadata() {
    return cluster.getMetadata().getKeyspaces().stream()
        .map(keyspace -> Tuple.of(keyspace.getName(), keyspace.getTables().stream()
            .map(AbstractTableMetadata::getName)
            .collect(Collectors.toList())))
        .collect(Collectors.toList());
  }

  public void copy(String keyspace, String sourceTable, String destinationTable) {

    var select = String.format("SELECT * FROM %s.%s WHERE token(%s) > ? AND token(%s) <= ?",
        keyspace, sourceTable, columnId, columnId);

    var selectStatement = session.prepare(select);

    var insert = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)",
        keyspace, destinationTable, columnId, columnData, columnTimestamp);

    var insertStatement = session.prepare(insert);
    // insertStatement.setConsistencyLevel(ConsistencyLevel.ONE);

    // perform full table scan in parallel using token ranges
    // optimal for copying large amounts of data
    cluster.getMetadata().getTokenRanges().stream()
        .flatMap(range -> range.unwrap().stream())
        .map(range -> selectStatement.bind(range.getStart(), range.getEnd()))
        .map(selectBoundStatement -> executorService.submit(() -> batchInsert(selectBoundStatement, insertStatement)))
        .forEach(this::awaitThread);

  }

  private void batchInsert(BoundStatement select, PreparedStatement insert) {
    // unlogged removes the log record for increased insert speed
    var batchStatement = new BatchStatement(BatchStatement.Type.UNLOGGED);

    session.execute(select).all().stream()
        .map(r -> Triplet.of(
            r.get(columnId, UUID.class),
            r.get(columnData, String.class),
            r.get(columnTimestamp, Date.class)))
        .map(t -> insert.bind(t.value1(), t.value2(), t.value3()))
        .forEach(batchStatement::add);

    session.execute(batchStatement);
  }

  private void awaitThread(Future<?> future) {
    try {
      future.get();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      LOGGER.error("Interrupted thread while copying data: ", e);
    } catch (ExecutionException e) {
      LOGGER.error("Error while copying data: ", e);
    }
  }

  @Override
  public void close() {
    // gracefully shutdown executor service
    executorService.shutdown();
    // close scylla session
    ScyllaSessionPool.closeSession(scyllaConfig);
  }

}
