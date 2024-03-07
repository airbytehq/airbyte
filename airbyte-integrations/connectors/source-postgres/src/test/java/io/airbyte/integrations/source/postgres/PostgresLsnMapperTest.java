/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.PostgresUtils;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.source.postgres.cdc.PostgresLsnMapper;
import io.debezium.connector.postgresql.connection.Lsn;
import java.sql.SQLException;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

public class PostgresLsnMapperTest {

  @Test
  public void LsnCommitTest() throws SQLException {
    final String plugin = "pgoutput";
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
      database.execute("CHECKPOINT");

      final var slotStateAtTheBeginning = getReplicationSlot(database, fullReplicationSlot, plugin, dbName);
      final Lsn lsnAtTheBeginning = Lsn.valueOf(slotStateAtTheBeginning.get("confirmed_flush_lsn").asText());

      final long targetLsn = PostgresUtils.getLsn(database).asLong();
      PostgresLsnMapper.commitLSNToPostgresDatabase(database,
          PgLsn.fromLong(targetLsn),
          fullReplicationSlot,
          publication,
          plugin);

      final var slotStateAfterCommit = getReplicationSlot(database, fullReplicationSlot, plugin, dbName);
      final Lsn lsnAfterCommit = Lsn.valueOf(slotStateAfterCommit.get("confirmed_flush_lsn").asText());

      Assertions.assertEquals(1, lsnAfterCommit.compareTo(lsnAtTheBeginning));
      Assertions.assertEquals(targetLsn, lsnAfterCommit.asLong());
      Assertions.assertNotEquals(slotStateAtTheBeginning, slotStateAfterCommit);

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

}
