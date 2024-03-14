/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.components.debezium.DebeziumComponentIntegrationTest;
import io.airbyte.cdk.components.debezium.DebeziumProducer;
import io.airbyte.cdk.components.debezium.DebeziumState;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.cdc.PostgresConverter;
import io.airbyte.integrations.source.postgres.cdc.PostgresDebeziumComponentUtils;
import io.airbyte.integrations.source.postgres.cdc.PostgresLsnMapper;
import io.debezium.connector.postgresql.PostgresConnector;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

public class PostgresDebeziumComponentIntegrationTest extends DebeziumComponentIntegrationTest {

  public PostgresDebeziumComponentIntegrationTest() {
    super(new PostgresLsnMapper());
  }

  private PostgresTestDatabase testdb;

  static final String CREATE_TABLE_KV = """
                                        CREATE TABLE kv (k SERIAL PRIMARY KEY, v VARCHAR(60));
                                        """;

  static final String CREATE_TABLE_EVENTLOG =
      """
      CREATE TABLE eventlog (id UUID GENERATED ALWAYS AS (MD5(entry)::UUID) STORED, entry VARCHAR(60) NOT NULL);
      ALTER TABLE eventlog REPLICA IDENTITY FULL;
      """;

  @Override
  public void applyToSource(@NotNull List<Change> changes) {
    for (var change : changes) {
      var sql = switch (change.kind()) {
        case INSERT -> String.format("INSERT INTO %s (%s) VALUES ('%s');",
            change.table(), change.table().getValueColumnName(), change.newValue());
        case DELETE -> String.format("DELETE FROM %s WHERE %s = '%s';",
            change.table(), change.table().getValueColumnName(), change.oldValue());
        case UPDATE -> String.format("UPDATE %s SET %s = '%s' WHERE %s = '%s';",
            change.table(),
            change.table().getValueColumnName(), change.newValue(),
            change.table().getValueColumnName(), change.oldValue());
      };
      testdb.with(sql);
    }
    testdb.with("CHECKPOINT");

  }

  @Override
  public void bulkInsertSourceKVTable(long numRows) {
    testdb.with("INSERT INTO kv (v) SELECT n::VARCHAR FROM GENERATE_SERIES(1, %d) AS n", numRows)
        .with("CHECKPOINT");
  }

  @NotNull
  @Override
  public DebeziumState currentSourceState() {
    try {
      final PgLsn lsn = PgLsn.fromPgString(testdb.getDatabase().query(ctx -> ctx
          .selectFrom("pg_current_wal_insert_lsn()")
          .fetchSingle(0, String.class)));
      long txid = testdb.getDatabase().query(ctx -> ctx
          .selectFrom("txid_current()")
          .fetchSingle(0, Long.class));
      var now = Instant.now();
      var value = new HashMap<String, Object>();
      value.put("transaction_id", null);
      value.put("lsn", lsn.asLong());
      value.put("txId", txid);
      value.put("ts_usec", now.toEpochMilli() * 1_000);
      var valueJson = Jsons.jsonNode(value);
      var keyJson = Jsons.arrayNode()
          .add(testdb.getDatabaseName())
          .add(Jsons.jsonNode(Map.of("server", testdb.getDatabaseName())));
      var offset = new DebeziumState.Offset(Map.of(keyJson, valueJson));
      return new DebeziumState(offset, Optional.empty());
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @NotNull
  @Override
  public DebeziumProducer.Builder producerBuilder() {
    return new DebeziumProducer.Builder()
        .withConnector(PostgresConnector.class)
        .with("plugin.name", "pgoutput")
        .with("publication.autocreate.mode", "disabled")
        .with("converters", "postgres_converter")
        .with("postgres_converter.type", PostgresConverter.class.getName())
        .with("include.unknown.datatypes", "true")
        .with("snapshot.mode", "initial")
        .with("max.queue.size.in.bytes", Long.toString(256L * 1024 * 1024))
        .withDatabaseHost(testdb.getContainer().getHost())
        .withDatabasePort(testdb.getContainer().getFirstMappedPort())
        .withDatabaseUser(testdb.getUserName())
        .withDatabasePassword(testdb.getPassword())
        .withDatabaseName(testdb.getDatabaseName())
        .withCatalog(configuredCatalog)
        .withHeartbeats(PostgresDebeziumComponentUtils.HEARTBEAT_INTERVAL_IN_TESTS)
        .with("slot.name", testdb.getReplicationSlotName())
        .with("publication.name", testdb.getPublicationName());
  }

  @BeforeEach
  void setup() {
    testdb = PostgresTestDatabase.in(PostgresTestDatabase.BaseImage.POSTGRES_16, PostgresTestDatabase.ContainerModifier.CONF)
        .with(CREATE_TABLE_KV)
        .with(CREATE_TABLE_EVENTLOG)
        .withReplicationSlot()
        .withPublicationForAllTables()
        .with("CHECKPOINT");
  }

  @AfterEach
  void tearDown() {
    if (testdb != null) {
      testdb.close();
      testdb = null;
    }
  }

}
