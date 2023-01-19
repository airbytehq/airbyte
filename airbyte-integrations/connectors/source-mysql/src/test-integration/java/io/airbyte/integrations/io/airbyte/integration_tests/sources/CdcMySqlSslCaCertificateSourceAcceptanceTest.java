/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.io.airbyte.integration_tests.sources.utils.TestConstants.INITIAL_CDC_WAITING_SECONDS;
import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.MySqlUtils;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class CdcMySqlSslCaCertificateSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private MySQLContainer<?> container;
  private JsonNode config;
  private static MySqlUtils.Certificate certs;

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
                String.format("%s", config.get(JdbcUtils.DATABASE_KEY).asText()),
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
                String.format("%s", config.get(JdbcUtils.DATABASE_KEY).asText()),
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
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();
    certs = MySqlUtils.getCertificate(container, true);

    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", "Passw0rd")
        .build();
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("initial_waiting_seconds", INITIAL_CDC_WAITING_SECONDS)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, true)
        .put(JdbcUtils.SSL_MODE_KEY, sslMode)
        .put("replication_method", replicationMethod)
        .put("is_test", true)
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
    try (final DSLContext dslContext = DSLContextFactory.create(
        "root",
        "test",
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()),
        SQLDialect.MYSQL)) {
      final Database database = new Database(dslContext);
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
  public void testIncrementalSyncShouldNotFailIfBinlogIsDeleted() throws Exception {
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
    final JsonNode latestState = Jsons.jsonNode(supportsPerStream() ? stateMessages : List.of(Iterables.getLast(stateMessages)));
    // RESET MASTER removes all binary log files that are listed in the index file,
    // leaving only a single, empty binary log file with a numeric suffix of .000001
    executeQuery("RESET MASTER;");

    assertEquals(6, filterRecords(runRead(configuredCatalog, latestState)).size());
  }

}
