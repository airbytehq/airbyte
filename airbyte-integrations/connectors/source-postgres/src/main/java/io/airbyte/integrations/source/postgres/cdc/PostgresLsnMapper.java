/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMMIT_LSN_KEY;
import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMPLETELY_PROCESSED_LSN_KEY;
import static io.debezium.connector.postgresql.SourceInfo.LSN_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.components.debezium.DebeziumComponent;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.kafka.connect.source.SourceRecord;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.postgresql.core.BaseConnection;
import org.postgresql.replication.LogSequenceNumber;
import org.postgresql.replication.PGReplicationStream;
import org.postgresql.replication.fluent.logical.ChainedLogicalStreamBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresLsnMapper implements DebeziumComponent.Config.LsnMapper<PgLsn> {

  @NotNull
  @Override
  public PgLsn get(@NotNull DebeziumComponent.State.Offset offset) {
    Preconditions.checkState(offset.debeziumOffset().size() == 1);
    var json = offset.debeziumOffset().values().iterator().next();
    if (json.has(LSN_KEY)) {
      return PgLsn.fromLong(json.get(LSN_KEY).asLong());
    }
    if (json.has(LAST_COMPLETELY_PROCESSED_LSN_KEY)) {
      return PgLsn.fromLong(json.get(LAST_COMPLETELY_PROCESSED_LSN_KEY).asLong());
    }
    if (json.has(LAST_COMMIT_LSN_KEY)) {
      return PgLsn.fromLong(json.get(LAST_COMMIT_LSN_KEY).asLong());
    }
    throw new IllegalStateException("debezium offset has no known LSN data: " + offset);
  }

  @Nullable
  @Override
  public PgLsn get(@NotNull DebeziumComponent.Record record) {
    if (!record.source().has("lsn")) {
      return null;
    }
    return PgLsn.fromLong(record.source().get("lsn").asLong());
  }

  @Nullable
  @Override
  public PgLsn get(@NotNull SourceRecord sourceRecord) {
    final Object lsnValue = sourceRecord.sourceOffset().get("lsn");
    if (lsnValue instanceof Long) {
      return PgLsn.fromLong((Long) lsnValue);
    }
    return null;
  }

  static private final Logger LOGGER = LoggerFactory.getLogger(PostgresLsnMapper.class);

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process WAL from a specific LSN and skip snapshot phase
   */
  static public DebeziumComponent.State makeSyntheticDebeziumState(JdbcDatabase database, String dbName) {
    final PgLsn lsn;
    final long txid;
    try {
      final List<JsonNode> rows = database.bufferedResultSetQuery(
          conn -> conn.createStatement().executeQuery("SELECT * FROM pg_current_wal_lsn(), txid_current()"),
          JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(rows.size() == 1);
      lsn = PgLsn.fromPgString(rows.getFirst().get("pg_current_wal_lsn").asText());
      txid = rows.getFirst().get("txid_current").asLong();
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
    LOGGER.info("Constructing initial debezium state for lsn = {}, txid = {}", lsn, txid);
    var now = Instant.now();
    var value = new HashMap<String, Object>();
    value.put("transaction_id", null);
    value.put("lsn", lsn.asLong());
    value.put("txId", txid);
    value.put("ts_usec", now.toEpochMilli() * 1_000);
    var valueJson = Jsons.jsonNode(value);
    var keyJson = Jsons.arrayNode()
        .add(dbName)
        .add(Jsons.jsonNode(Map.of("server", dbName)));
    var offset = new DebeziumComponent.State.Offset(Map.of(keyJson, valueJson));
    return new DebeziumComponent.State(offset, Optional.empty());
  }

  static public boolean isSavedOffsetAfterReplicationSlotLSN(JsonNode replicationSlot, PgLsn savedOffset) {
    if (replicationSlot.has("confirmed_flush_lsn")) {
      final var confirmedFlushLsnOnServerSide = PgLsn.fromPgString(replicationSlot.get("confirmed_flush_lsn").asText());
      LOGGER.info("Replication slot confirmed_flush_lsn : " + confirmedFlushLsnOnServerSide + " Saved offset LSN : " + savedOffset);
      return savedOffset.compareTo(confirmedFlushLsnOnServerSide) >= 0;
    } else if (replicationSlot.has("restart_lsn")) {
      final var restartLsn = PgLsn.fromPgString(replicationSlot.get("restart_lsn").asText());
      LOGGER.info("Replication slot restart_lsn : " + restartLsn + " Saved offset LSN : " + savedOffset);
      return savedOffset.compareTo(restartLsn) >= 0;
    }

    // We return true when saved offset is not present cause using an empty offset would result in sync
    // from scratch anyway
    return true;
  }

  static public void commitLSNToPostgresDatabase(JdbcDatabase jdbcDatabase,
                                                 PgLsn savedOffset,
                                                 String slotName,
                                                 String publicationName,
                                                 String plugin) {
    final var jdbcConfig = jdbcDatabase.getDatabaseConfig();
    final LogSequenceNumber logSequenceNumber = LogSequenceNumber.valueOf(savedOffset.asLong());

    try (final BaseConnection pgConnection = (BaseConnection) PostgresReplicationConnection.createConnection(jdbcConfig)) {
      ChainedLogicalStreamBuilder streamBuilder = pgConnection
          .getReplicationAPI()
          .replicationStream()
          .logical()
          .withSlotName("\"" + slotName + "\"")
          .withStartPosition(logSequenceNumber);

      streamBuilder = addSlotOption(publicationName, plugin, pgConnection, streamBuilder);

      try (final PGReplicationStream stream = streamBuilder.start()) {
        stream.forceUpdateStatus();

        stream.setFlushedLSN(logSequenceNumber);
        stream.setAppliedLSN(logSequenceNumber);

        stream.forceUpdateStatus();
      }
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  static private ChainedLogicalStreamBuilder addSlotOption(String publicationName,
                                                           String plugin,
                                                           BaseConnection pgConnection,
                                                           ChainedLogicalStreamBuilder streamBuilder) {
    if (plugin.equalsIgnoreCase("pgoutput")) {
      streamBuilder = streamBuilder.withSlotOption("proto_version", 1)
          .withSlotOption("publication_names", publicationName);

      if (pgConnection.haveMinimumServerVersion(140000)) {
        streamBuilder = streamBuilder.withSlotOption("messages", true);
      }
    } else {
      throw new RuntimeException("Unknown plugin value : " + plugin);
    }
    return streamBuilder;
  }

}
