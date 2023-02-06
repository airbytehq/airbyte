/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import static io.airbyte.integrations.source.mysql.MySqlSource.SSL_PARAMETERS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.MySqlUtils;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.*;
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
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asText(),
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

  @Override
  protected void incrementalDateCheck() throws Exception {
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        List.of(getTestMessages().get(1), getTestMessages().get(2)));
  }

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return List.of(
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19")))));
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19")))));
    final DbStreamState state = new DbStreamState()
        .withStreamName(streamName)
        .withStreamNamespace(namespace)
        .withCursorField(List.of(COL_ID))
        .withCursor("5")
        .withCursorRecordCount(1L);
    expectedMessages.addAll(createExpectedTestMessages(List.of(state)));
    return expectedMessages;
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
          .put(JdbcUtils.SSL_MODE_KEY, Map.of(JdbcUtils.MODE_KEY, "disable")));

      final AirbyteConnectionStatus actual = source.check(configWithSSLModeDisabled);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, actual.getStatus());
    } finally {
      bastion.stopAndClose();
    }
  }

  @Override
  protected boolean supportsPerStream() {
    return true;
  }

}
