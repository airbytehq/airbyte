/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import static io.airbyte.integrations.source.mysql.MySqlSource.SSL_PARAMETERS;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.STATE_TYPE_KEY;
import static java.util.stream.Collectors.toList;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.MySqlUtils;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.integrations.source.mysql.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.mysql.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.Network;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
class MySqlStrictEncryptJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  protected static final String TEST_USER = "test";
  protected static final String TEST_PASSWORD = "test";
  protected static MySQLContainer<?> container;
  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();

  protected Database database;
  protected DSLContext dslContext;

  @BeforeAll
  static void init() throws SQLException {
    container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD);
    container.start();
    final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), "root", container.getPassword());
    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
  }

  @BeforeEach
  public void setup() throws Exception {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, Strings.addRandomSuffix("db", "_", 10))
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s?%s",
            container.getHost(),
            container.getFirstMappedPort(),
            String.join("&", SSL_PARAMETERS)),
        SQLDialect.MYSQL);
    database = new Database(dslContext);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get(JdbcUtils.DATABASE_KEY).asText());
      return null;
    });

    super.setup();
  }

  @AfterEach
  void tearDownMySql() throws Exception {
    dslContext.close();
    super.tearDown();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  // MySql does not support schemas in the way most dbs do. Instead we namespace by db name.
  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public MySqlSource getJdbcSource() {
    return new MySqlSource();
  }

  @Override
  public Source getSource() {
    return new MySqlStrictEncryptSource();
  }

  @Override
  public String getDriverClass() {
    return MySqlSource.DRIVER_CLASS;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Test
  void testStrictSSLUnsecuredNoTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "preferred")
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Unsecured connection not allowed"));
  }

  @Test
  void testStrictSSLSecuredNoTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", PASSWORD)
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "NO_TUNNEL")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertFalse(actual.getMessage().contains("Unsecured connection not allowed"));
  }

  @Test
  void testStrictSSLSecuredWithTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "verify_ca")
        .put("ca_certificate", certs.getCaCertificate())
        .put("client_certificate", certs.getClientCertificate())
        .put("client_key", certs.getClientKey())
        .put("client_key_password", PASSWORD)
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "SSH_KEY_AUTH")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."));
  }

  @Test
  void testStrictSSLUnsecuredWithTunnel() throws Exception {
    final String PASSWORD = "Passw0rd";
    final var certs = MySqlUtils.getCertificate(container, true);
    final var sslMode = ImmutableMap.builder()
        .put(JdbcUtils.MODE_KEY, "preferred")
        .build();

    final var tunnelMode = ImmutableMap.builder()
        .put("tunnel_method", "SSH_KEY_AUTH")
        .build();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake")
        .put(JdbcUtils.SSL_KEY, true)
        .putIfAbsent(JdbcUtils.SSL_MODE_KEY, Jsons.jsonNode(sslMode));
    ((ObjectNode) config).putIfAbsent("tunnel_method", Jsons.jsonNode(tunnelMode));

    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
    assertTrue(actual.getMessage().contains("Could not connect with provided SSH configuration."));
  }

  @Test
  void testCheckWithSSlModeDisabled() throws Exception {
    try (final MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0").withNetwork(network)) {
      bastion.initAndStartBastion(network);
      db.start();
      final JsonNode configWithSSLModeDisabled = bastion.getTunnelConfig(SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH, ImmutableMap.builder()
          .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(db.getContainerInfo()
              .getNetworkSettings()
              .getNetworks()
              .entrySet().stream()
              .findFirst()
              .get().getValue().getIpAddress()))
          .put(JdbcUtils.PORT_KEY, db.getExposedPorts().get(0))
          .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
          .put(JdbcUtils.SCHEMAS_KEY, List.of("public"))
          .put(JdbcUtils.USERNAME_KEY, db.getUsername())
          .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
          .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, "disable")), false);

      final AirbyteConnectionStatus actual = source.check(configWithSSLModeDisabled);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, actual.getStatus());
    } finally {
      bastion.stopAndClose();
    }
  }

  @Test
  void testReadMultipleTablesIncrementally() throws Exception {
    ((ObjectNode) config).put("sync_checkpoint_records", 1);
    final String namespace = getDefaultNamespace();
    final String streamOneName = TABLE_NAME + "one";
    // Create a fresh first table
    database.query(connection -> {
      connection.fetch(String.format("USE %s;", getDefaultNamespace()));
      connection.fetch(String.format("CREATE TABLE %s (\n"
          + "    id int PRIMARY KEY,\n"
          + "    name VARCHAR(200) NOT NULL,\n"
          + "    updated_at VARCHAR(200) NOT NULL\n"
          + ");", streamOneName));
      connection.execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at) VALUES (1,'picard', '2004-10-19')",
              getFullyQualifiedTableName(streamOneName)));
      connection.execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
              getFullyQualifiedTableName(streamOneName)));
      connection.execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
              getFullyQualifiedTableName(streamOneName)));
      return null;
    });

    // Create a fresh second table
    final String streamTwoName = TABLE_NAME + "two";
    final String streamTwoFullyQualifiedName = getFullyQualifiedTableName(streamTwoName);
    // Insert records into second table
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE TABLE %s (\n"
          + "    id int PRIMARY KEY,\n"
          + "    name VARCHAR(200) NOT NULL,\n"
          + "    updated_at DATE NOT NULL\n"
          + ");", streamTwoName));
      ctx.execute(
          String.format("INSERT INTO %s(id, name, updated_at)"
              + "VALUES (40,'Jean Luc','2006-10-19')",
              streamTwoFullyQualifiedName));
      ctx.execute(
          String.format("INSERT INTO %s(id, name, updated_at)"
              + "VALUES (41, 'Groot', '2006-10-19')",
              streamTwoFullyQualifiedName));
      ctx.execute(
          String.format("INSERT INTO %s(id, name, updated_at)"
              + "VALUES (42, 'Thanos','2006-10-19')",
              streamTwoFullyQualifiedName));
      return null;
    });
    // Create records list that we expect to see in the state message
    final List<AirbyteMessage> streamTwoExpectedRecords = Arrays.asList(
        createRecord(streamTwoName, namespace, ImmutableMap.of(
            COL_ID, 40,
            COL_NAME, "Jean Luc",
            COL_UPDATED_AT, "2006-10-19")),
        createRecord(streamTwoName, namespace, ImmutableMap.of(
            COL_ID, 41,
            COL_NAME, "Groot",
            COL_UPDATED_AT, "2006-10-19")),
        createRecord(streamTwoName, namespace, ImmutableMap.of(
            COL_ID, 42,
            COL_NAME, "Thanos",
            COL_UPDATED_AT, "2006-10-19")));

    // Prep and create a configured catalog to perform sync
    final AirbyteStream streamOne = getAirbyteStream(streamOneName, namespace);
    final AirbyteStream streamTwo = getAirbyteStream(streamTwoName, namespace);

    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        new AirbyteCatalog().withStreams(List.of(streamOne, streamTwo)));
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(List.of(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
      airbyteStream.withPrimaryKey(List.of(List.of(COL_ID)));
    });

    // Perform initial sync
    final List<AirbyteMessage> messagesFromFirstSync = MoreIterators
        .toList(source.read(config, configuredCatalog, null));

    final List<AirbyteMessage> recordsFromFirstSync = filterRecords(messagesFromFirstSync);

    setEmittedAtToNull(messagesFromFirstSync);
    // All records in the 2 configured streams should be present
    assertThat(filterRecords(recordsFromFirstSync)).containsExactlyElementsOf(
        Stream.concat(getTestMessages(streamOneName).stream().parallel(),
            streamTwoExpectedRecords.stream().parallel()).collect(toList()));

    final List<AirbyteStateMessage> actualFirstSyncState = extractStateMessage(messagesFromFirstSync);
    // Since we are emitting a state message after each record, we should have 1 state for each record -
    // 3 from stream1 and 3 from stream2
    assertEquals(6, actualFirstSyncState.size());

    // The expected state type should be 2 primaryKey's and the last one being standard
    final List<String> expectedStateTypesFromFirstSync = List.of("primary_key", "primary_key", "cursor_based");
    final List<String> stateTypeOfStreamOneStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, STATE_TYPE_KEY);
    final List<String> stateTypeOfStreamTwoStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamTwoName, STATE_TYPE_KEY);
    // It should be the same for stream1 and stream2
    assertEquals(stateTypeOfStreamOneStatesFromFirstSync, expectedStateTypesFromFirstSync);
    assertEquals(stateTypeOfStreamTwoStatesFromFirstSync, expectedStateTypesFromFirstSync);

    // Create the expected primaryKeys that we should see
    final List<String> expectedPrimaryKeysFromFirstSync = List.of("1", "2");
    final List<String> primaryKeyFromStreamOneStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, "pk_val");
    final List<String> primaryKeyFromStreamTwoStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, "pk_val");

    // Verifying each element and its index to match.
    // Only checking the first 2 elements since we have verified that the last state_type is
    // "cursor_based"
    assertEquals(primaryKeyFromStreamOneStatesFromFirstSync.get(0), expectedPrimaryKeysFromFirstSync.get(0));
    assertEquals(primaryKeyFromStreamOneStatesFromFirstSync.get(1), expectedPrimaryKeysFromFirstSync.get(1));
    assertEquals(primaryKeyFromStreamTwoStatesFromFirstSync.get(0), expectedPrimaryKeysFromFirstSync.get(0));
    assertEquals(primaryKeyFromStreamTwoStatesFromFirstSync.get(1), expectedPrimaryKeysFromFirstSync.get(1));

    // Extract only state messages for each stream
    final List<AirbyteStateMessage> streamOneStateMessagesFromFirstSync = extractStateMessage(messagesFromFirstSync, streamOneName);
    final List<AirbyteStateMessage> streamTwoStateMessagesFromFirstSync = extractStateMessage(messagesFromFirstSync, streamTwoName);
    // Extract the incremental states of each stream's first and second state message
    final List<JsonNode> streamOneIncrementalStatesFromFirstSync =
        List.of(streamOneStateMessagesFromFirstSync.get(0).getStream().getStreamState().get("incremental_state"),
            streamOneStateMessagesFromFirstSync.get(1).getStream().getStreamState().get("incremental_state"));
    final JsonNode streamOneFinalStreamStateFromFirstSync = streamOneStateMessagesFromFirstSync.get(2).getStream().getStreamState();

    final List<JsonNode> streamTwoIncrementalStatesFromFirstSync =
        List.of(streamTwoStateMessagesFromFirstSync.get(0).getStream().getStreamState().get("incremental_state"),
            streamTwoStateMessagesFromFirstSync.get(1).getStream().getStreamState().get("incremental_state"));
    final JsonNode streamTwoFinalStreamStateFromFirstSync = streamTwoStateMessagesFromFirstSync.get(2).getStream().getStreamState();

    // The incremental_state of each stream's first and second incremental states is expected
    // to be identical to the stream_state of the final state message for each stream
    assertEquals(streamOneIncrementalStatesFromFirstSync.get(0), streamOneFinalStreamStateFromFirstSync);
    assertEquals(streamOneIncrementalStatesFromFirstSync.get(1), streamOneFinalStreamStateFromFirstSync);
    assertEquals(streamTwoIncrementalStatesFromFirstSync.get(0), streamTwoFinalStreamStateFromFirstSync);
    assertEquals(streamTwoIncrementalStatesFromFirstSync.get(1), streamTwoFinalStreamStateFromFirstSync);

    // Sync should work with a primaryKey state AND a cursor-based state from each stream
    // Forcing a sync with
    // - stream one state still being the first record read via Primary Key.
    // - stream two state being the Primary Key state before the final emitted state before the cursor
    // switch
    final List<AirbyteMessage> messagesFromSecondSyncWithMixedStates = MoreIterators
        .toList(source.read(config, configuredCatalog,
            Jsons.jsonNode(List.of(streamOneStateMessagesFromFirstSync.get(0),
                streamTwoStateMessagesFromFirstSync.get(1)))));

    // Extract only state messages for each stream after second sync
    final List<AirbyteStateMessage> streamOneStateMessagesFromSecondSync =
        extractStateMessage(messagesFromSecondSyncWithMixedStates, streamOneName);
    final List<String> stateTypeOfStreamOneStatesFromSecondSync =
        extractSpecificFieldFromCombinedMessages(messagesFromSecondSyncWithMixedStates, streamOneName, STATE_TYPE_KEY);

    final List<AirbyteStateMessage> streamTwoStateMessagesFromSecondSync =
        extractStateMessage(messagesFromSecondSyncWithMixedStates, streamTwoName);
    final List<String> stateTypeOfStreamTwoStatesFromSecondSync =
        extractSpecificFieldFromCombinedMessages(messagesFromSecondSyncWithMixedStates, streamTwoName, STATE_TYPE_KEY);

    // Stream One states after the second sync are expected to have 2 stream states
    // - 1 with PrimaryKey state_type and 1 state that is of cursorBased state type
    assertEquals(2, streamOneStateMessagesFromSecondSync.size());
    assertEquals(List.of("primary_key", "cursor_based"), stateTypeOfStreamOneStatesFromSecondSync);

    // Stream Two states after the second sync are expected to have 1 stream state
    // - The state that is of cursorBased state type
    assertEquals(1, streamTwoStateMessagesFromSecondSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamTwoStatesFromSecondSync);

    // Add some data to each table and perform a third read.
    // Expect to see all records be synced via cursorBased method and not primaryKey

    database.query(ctx -> {
      ctx.execute(
          String.format("INSERT INTO %s(id, name, updated_at)"
              + "VALUES (4,'Hooper','2006-10-19')",
              getFullyQualifiedTableName(streamOneName)));
      ctx.execute(
          String.format("INSERT INTO %s(id, name, updated_at)"
              + "VALUES (43, 'Iron Man', '2006-10-19')",
              streamTwoFullyQualifiedName));
      return null;
    });

    final List<AirbyteMessage> messagesFromThirdSync = MoreIterators
        .toList(source.read(config, configuredCatalog,
            Jsons.jsonNode(List.of(streamOneStateMessagesFromSecondSync.get(1),
                streamTwoStateMessagesFromSecondSync.get(0)))));

    // Extract only state messages, state type, and cursor for each stream after second sync
    final List<AirbyteStateMessage> streamOneStateMessagesFromThirdSync =
        extractStateMessage(messagesFromThirdSync, streamOneName);
    final List<String> stateTypeOfStreamOneStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamOneName, STATE_TYPE_KEY);
    final List<String> cursorOfStreamOneStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamOneName, "cursor");

    final List<AirbyteStateMessage> streamTwoStateMessagesFromThirdSync =
        extractStateMessage(messagesFromThirdSync, streamTwoName);
    final List<String> stateTypeOfStreamTwoStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamTwoName, STATE_TYPE_KEY);
    final List<String> cursorOfStreamTwoStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamTwoName, "cursor");

    // Both streams should now be synced via standard cursor and have updated max cursor values
    // cursor: 4 for stream one
    // cursor: 43 for stream two
    assertEquals(1, streamOneStateMessagesFromThirdSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamOneStatesFromThirdSync);
    assertEquals(List.of("4"), cursorOfStreamOneStatesFromThirdSync);

    assertEquals(1, streamTwoStateMessagesFromThirdSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamTwoStatesFromThirdSync);
    assertEquals(List.of("43"), cursorOfStreamTwoStatesFromThirdSync);
  }

  @Override
  protected boolean supportsPerStream() {
    return true;
  }

  // Override from parent class as we're no longer including the legacy Data field.
  @Override
  protected List<AirbyteMessage> createExpectedTestMessages(final List<DbStreamState> states) {
    return supportsPerStream()
        ? states.stream()
            .map(s -> new AirbyteMessage().withType(Type.STATE)
                .withState(
                    new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
                        .withStream(new AirbyteStreamState()
                            .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                            .withStreamState(Jsons.jsonNode(s)))))
            .collect(
                Collectors.toList())
        : List.of(new AirbyteMessage().withType(Type.STATE).withState(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY)));
  }

  @Override
  protected List<AirbyteStateMessage> createState(final List<DbStreamState> states) {
    return supportsPerStream()
        ? states.stream()
            .map(s -> new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                    .withStreamState(Jsons.jsonNode(s))))
            .collect(
                Collectors.toList())
        : List.of(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY));
  }

  @Override
  protected JsonNode getStateData(final AirbyteMessage airbyteMessage, final String streamName) {
    final JsonNode streamState = airbyteMessage.getState().getStream().getStreamState();
    if (streamState.get("stream_name").asText().equals(streamName)) {
      return streamState;
    }

    throw new IllegalArgumentException("Stream not found in state message: " + streamName);
  }

  @Override
  protected DbStreamState buildStreamState(final ConfiguredAirbyteStream configuredAirbyteStream,
                                           final String cursorField,
                                           final String cursorValue) {
    return new CursorBasedStatus().withStateType(StateType.CURSOR_BASED).withVersion(2L)
        .withStreamName(configuredAirbyteStream.getStream().getName())
        .withStreamNamespace(configuredAirbyteStream.getStream().getNamespace())
        .withCursorField(List.of(cursorField))
        .withCursor(cursorValue)
        .withCursorRecordCount(1L);
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19")))));
    final DbStreamState state = new CursorBasedStatus()
        .withStateType(StateType.CURSOR_BASED)
        .withVersion(2L)
        .withStreamName(streamName)
        .withStreamNamespace(namespace)
        .withCursorField(ImmutableList.of(COL_ID))
        .withCursor("5")
        .withCursorRecordCount(1L);

    expectedMessages.addAll(createExpectedTestMessages(List.of(state)));
    return expectedMessages;
  }

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return getTestMessages(streamName);
  }

  protected List<AirbyteMessage> getTestMessages(final String streamName) {
    return List.of(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19")))));
  }

  private AirbyteStream getAirbyteStream(final String tableName, final String namespace) {
    return CatalogHelpers.createAirbyteStream(
        tableName,
        namespace,
        Field.of(COL_ID, JsonSchemaType.INTEGER),
        Field.of(COL_NAME, JsonSchemaType.STRING),
        Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID)));
  }

}
