/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.internals.postgres.PostgresDebeziumStateUtil;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.debezium.connector.postgresql.connection.Lsn;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.OptionalLong;
import java.util.Properties;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

public class PostgresDebeziumStateUtilTest {

  private static final JsonNode REPLICATION_METHOD = Jsons.jsonNode(ImmutableMap.builder()
      .put("replication_slot", "replication_slot")
      .put("publication", "publication")
      .put("plugin", "pgoutput")
      .build());

  private static final JsonNode CONFIG = Jsons.jsonNode(ImmutableMap.builder()
      .put(JdbcUtils.HOST_KEY, "host")
      .put(JdbcUtils.PORT_KEY, "5432")
      .put(JdbcUtils.DATABASE_KEY, "db_jagkjrgxhw")
      .put(JdbcUtils.SCHEMAS_KEY, List.of("schema_1", "schema_2"))
      .put(JdbcUtils.USERNAME_KEY, "username")
      .put(JdbcUtils.PASSWORD_KEY, "password")
      .put(JdbcUtils.SSL_KEY, false)
      .put("replication_method", REPLICATION_METHOD)
      .build());

  // Lsn.valueOf("0/16CA330") = 23896880
  // Lsn.valueOf("0/16CA368") = 23896936
  private static final JsonNode REPLICATION_SLOT = Jsons.jsonNode(ImmutableMap.builder()
      .put("confirmed_flush_lsn", "0/16CA368")
      .put("restart_lsn", "0/16CA330")
      .build());

  private final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

  @ParameterizedTest
  @ValueSource(strings = {
    "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23897640,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23897640,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]\":\"{\\\"transaction_id\\\":null,\\\"lsn\\\":23897640,\\\"txId\\\":505,\\\"ts_usec\\\":1677520006097984}\"}"})
  public void stateGeneratedAfterSnapshotCompletionAfterReplicationSlot(final String cdcState) {
    final JsonNode cdcStateAsJson = Jsons.deserialize(cdcState);

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcStateAsJson, CONFIG);
    Assertions.assertTrue(savedOffset.isPresent());
    Assertions.assertEquals(savedOffset.getAsLong(), 23897640L);

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, savedOffset);
    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @ParameterizedTest
  @ValueSource(strings = {
    "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23896935,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23896935,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]\":\"{\\\"transaction_id\\\":null,\\\"lsn\\\":23896935,\\\"txId\\\":505,\\\"ts_usec\\\":1677520006097984}\"}"})
  public void stateGeneratedAfterSnapshotCompletionBeforeReplicationSlot(final String cdcState) {
    final JsonNode cdcStateAsJson = Jsons.deserialize(cdcState);

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcStateAsJson, CONFIG);
    Assertions.assertTrue(savedOffset.isPresent());
    Assertions.assertEquals(savedOffset.getAsLong(), 23896935L);

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, savedOffset);
    Assertions.assertFalse(savedOffsetAfterReplicationSlotLSN);
  }

  @ParameterizedTest
  @ValueSource(strings = {
    "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23901120,\\\"lsn_commit\\\":23901120,\\\"lsn\\\":23901120,\\\"txId\\\":525,\\\"ts_usec\\\":1659422649959099}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23901120,\\\"lsn_commit\\\":23901120,\\\"lsn\\\":23901120,\\\"txId\\\":526,\\\"ts_usec\\\":1677531340598453}\"}"
  })
  public void stateGeneratedFromWalStreamingAfterReplicationSlot(final String cdcState) {
    final JsonNode cdcStateAsJson = Jsons.deserialize(cdcState);

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcStateAsJson, CONFIG);
    Assertions.assertTrue(savedOffset.isPresent());
    Assertions.assertEquals(savedOffset.getAsLong(), 23901120L);

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, savedOffset);
    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @ParameterizedTest
  @ValueSource(strings = {
    "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23896935,\\\"lsn_commit\\\":23896935,\\\"lsn\\\":23896935,\\\"txId\\\":525,\\\"ts_usec\\\":1659422649959099}\"}",
    "{\"[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23896935,\\\"lsn_commit\\\":23896935,\\\"lsn\\\":23896935,\\\"txId\\\":526,\\\"ts_usec\\\":1677531340598453}\"}"
  })
  public void stateGeneratedFromWalStreamingBeforeReplicationSlot(final String cdcState) {
    final JsonNode cdcStateAsJson = Jsons.deserialize(cdcState);

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcStateAsJson, CONFIG);
    Assertions.assertTrue(savedOffset.isPresent());
    Assertions.assertEquals(savedOffset.getAsLong(), 23896935L);

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, savedOffset);
    Assertions.assertFalse(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void nullOffset() {
    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, null);
    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void emptyState() {
    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(new Properties(),
        new ConfiguredAirbyteCatalog(), null, CONFIG);
    Assertions.assertTrue(savedOffset.isEmpty());

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(REPLICATION_SLOT, savedOffset);
    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @ParameterizedTest
  @ValueSource(strings = {"pgoutput", "wal2json"})
  public void LsnCommitTest(final String plugin) throws SQLException {
    final DockerImageName myImage = DockerImageName.parse("debezium/postgres:13-alpine").asCompatibleSubstituteFor("postgres");
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    final String fullReplicationSlot = "debezium_slot" + "_" + dbName;
    final String publication = "publication";
    try (final PostgreSQLContainer<?> container = new PostgreSQLContainer<>(myImage)) {
      container.start();

      final String initScriptName = "init_" + dbName.concat(".sql");
      final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
      PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

      final Map<String, String> databaseConfig = Map.of(JdbcUtils.USERNAME_KEY, container.getUsername(),
          JdbcUtils.PASSWORD_KEY, container.getPassword(),
          JdbcUtils.JDBC_URL_KEY, String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
              container.getHost(),
              container.getFirstMappedPort(),
              dbName));

      final JdbcDatabase database = new DefaultJdbcDatabase(
          DataSourceFactory.create(
              databaseConfig.get(JdbcUtils.USERNAME_KEY),
              databaseConfig.get(JdbcUtils.PASSWORD_KEY),
              DatabaseDriver.POSTGRESQL.getDriverClassName(),
              databaseConfig.get(JdbcUtils.JDBC_URL_KEY)));

      database.execute("SELECT pg_create_logical_replication_slot('" + fullReplicationSlot + "', '" + plugin + "');");
      database.execute("CREATE PUBLICATION " + publication + " FOR ALL TABLES;");

      database.execute("CREATE TABLE public.test_table (id int primary key, name varchar(256));");
      database.execute("insert into public.test_table values (1, 'foo');");
      database.execute("insert into public.test_table values (2, 'bar');");

      final Lsn lsnAtTheBeginning = Lsn.valueOf(
          getReplicationSlot(database, fullReplicationSlot, plugin, dbName).get("confirmed_flush_lsn").asText());

      final long targetLsn = PostgresUtils.getLsn(database).asLong();
      postgresDebeziumStateUtil.commitLSNToPostgresDatabase(Jsons.jsonNode(databaseConfig),
          OptionalLong.of(targetLsn),
          fullReplicationSlot,
          publication,
          plugin);

      final Lsn lsnAfterCommit = Lsn.valueOf(
          getReplicationSlot(database, fullReplicationSlot, plugin, dbName).get("confirmed_flush_lsn").asText());

      Assertions.assertEquals(1, lsnAfterCommit.compareTo(lsnAtTheBeginning));
      Assertions.assertEquals(targetLsn, lsnAfterCommit.asLong());
      container.stop();
    }
  }

  private JsonNode getReplicationSlot(final JdbcDatabase database, String slotName, String plugin, String dbName) {
    try {
      return database.queryJsons("SELECT * FROM pg_replication_slots WHERE slot_name = ? AND plugin = ? AND database = ?", slotName, plugin, dbName)
          .get(0);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  public void formatTest() {
    final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();
    final JsonNode debeziumState = postgresDebeziumStateUtil.format(23904232L, 506L, "db_fgnfxvllud", Instant.parse("2023-06-06T08:36:10.341842Z"));
    final Map<String, String> stateAsMap = Jsons.object(debeziumState, Map.class);
    Assertions.assertEquals(1, stateAsMap.size());
    Assertions.assertTrue(stateAsMap.containsKey("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));
    Assertions.assertEquals("{\"transaction_id\":null,\"lsn\":23904232,\"txId\":506,\"ts_usec\":1686040570341842}",
        stateAsMap.get("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));

  }

  @Test
  public void debeziumInitialStateConstructTest() {
    final DockerImageName myImage = DockerImageName.parse("debezium/postgres:13-alpine").asCompatibleSubstituteFor("postgres");
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    try (final PostgreSQLContainer<?> container = new PostgreSQLContainer<>(myImage)) {
      container.start();

      final String initScriptName = "init_" + dbName.concat(".sql");
      final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
      PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

      final Map<String, String> databaseConfig = Map.of(JdbcUtils.USERNAME_KEY, container.getUsername(),
          JdbcUtils.PASSWORD_KEY, container.getPassword(),
          JdbcUtils.JDBC_URL_KEY, String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
              container.getHost(),
              container.getFirstMappedPort(),
              dbName));

      final JdbcDatabase database = new DefaultJdbcDatabase(
          DataSourceFactory.create(
              databaseConfig.get(JdbcUtils.USERNAME_KEY),
              databaseConfig.get(JdbcUtils.PASSWORD_KEY),
              DatabaseDriver.POSTGRESQL.getDriverClassName(),
              databaseConfig.get(JdbcUtils.JDBC_URL_KEY)));

      final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();
      final JsonNode debeziumState = postgresDebeziumStateUtil.constructInitialDebeziumState(database, dbName);
      final Map<String, String> stateAsMap = Jsons.object(debeziumState, Map.class);
      Assertions.assertEquals(1, stateAsMap.size());
      Assertions.assertTrue(stateAsMap.containsKey("[\"" + dbName + "\",{\"server\":\"" + dbName + "\"}]"));
      Assertions.assertNotNull(stateAsMap.get("[\"" + dbName + "\",{\"server\":\"" + dbName + "\"}]"));
      container.stop();
    }
  }

}
