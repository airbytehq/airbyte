/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.protocol.models.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.source.mysql.MySqlSource.ReplicationMethod;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class CdcMySqlSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private MySQLContainer<?> container;
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s", STREAM_NAME),
                String.format("%s", config.get("database").asText()),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s", STREAM_NAME2),
                String.format("%s", config.get("database").asText()),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return null;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", ReplicationMethod.CDC)
        .build());

    revokeAllPermissions();
    grantCorrectPermissions();
    createAndPopulateTables();
  }

  private void createAndPopulateTables() {
    executeQuery("CREATE TABLE id_and_name(id INTEGER PRIMARY KEY, name VARCHAR(200));");
    executeQuery(
        "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    executeQuery("CREATE TABLE starships(id INTEGER PRIMARY KEY, name VARCHAR(200));");
    executeQuery(
        "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery(
        "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO "
            + container.getUsername() + "@'%';");
  }

  private void executeQuery(final String query) {
    final DSLContext dslContext = DSLContextFactory.create(
        "root",
        "test",
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()), SQLDialect.MYSQL);
    try (final Database database = new Database(dslContext)) {
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Test
  public void testIncrementalSyncFailedIfBinlogIsDeleted() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = withSourceDefinedCursors(getConfiguredCatalog());
    // only sync incremental streams
    configuredCatalog.setStreams(
        configuredCatalog.getStreams().stream().filter(s -> s.getSyncMode() == INCREMENTAL).collect(Collectors.toList()));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalog, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());
    assertFalse(recordMessages.isEmpty(), "Expected the first incremental sync to produce records");
    assertFalse(stateMessages.isEmpty(), "Expected incremental sync to produce STATE messages");

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    final JsonNode latestState = stateMessages.get(stateMessages.size() - 1).getData();
    // RESET MASTER removes all binary log files that are listed in the index file,
    // leaving only a single, empty binary log file with a numeric suffix of .000001
    executeQuery("RESET MASTER;");
    assertThrows(Exception.class, () -> filterRecords(runRead(configuredCatalog, latestState)));
  }

}
