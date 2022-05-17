/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.testcontainers.containers.Network;

public abstract class SshOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new OracleNameTransformer();

  private final String schemaName = "TEST_ORCL";

  private final SshBastionContainer sshBastionContainer = new SshBastionContainer();

  private OracleContainer db;

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle:dev";
  }

  @Override
  protected JsonNode getConfig() throws IOException, InterruptedException {
    return sshBastionContainer.getTunnelConfig(getTunnelMethod(),
        getBasicOracleDbConfigBuilder(db).put("schema", schemaName));
  }

  public ImmutableMap.Builder<Object, Object> getBasicOracleDbConfigBuilder(final OracleContainer db) {
    return ImmutableMap.builder()
        .put("host", Objects.requireNonNull(db.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .get(((Network.NetworkImpl) sshBastionContainer.getNetWork()).getName())
            .getIpAddress()))
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("port", db.getExposedPorts().get(0))
        .put("sid", db.getSid())
        .put("schemas", List.of("JDBC_SPACE"))
        .put("encryption", Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()));
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new OracleTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final List<JsonNode> jsonNodes = retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace);
    return jsonNodes
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase()).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        OracleDestination.HOST_KEY,
        OracleDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, OracleDestination.COLUMN_NAME_EMITTED_AT)))
            .stream()
            .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
            .map(Jsons::deserialize)
            .collect(Collectors.toList()));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    startTestContainers();
    SshTunnel.sshWrap(
        getConfig(),
        OracleDestination.HOST_KEY,
        OracleDestination.PORT_KEY,
        mangledConfig -> {
          final Database databaseFromConfig = getDatabaseFromConfig(mangledConfig);
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("CREATE USER %s IDENTIFIED BY %s", schemaName, schemaName)));
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("GRANT ALL PRIVILEGES TO %s", schemaName)));
        });
  }

  private void startTestContainers() {
    sshBastionContainer.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new OracleContainer()
        .withUsername("test")
        .withPassword("oracle")
        .usingSid()
        .withNetwork(sshBastionContainer.getNetWork());
    db.start();
  }

  private Database getDatabaseFromConfig(final JsonNode config) {
    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(), config.get("password").asText(), DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("sid").asText()), null);
    return new Database(dslContext);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    SshTunnel.sshWrap(
        getConfig(),
        OracleDestination.HOST_KEY,
        OracleDestination.PORT_KEY,
        mangledConfig -> {
          final Database databaseFromConfig = getDatabaseFromConfig(mangledConfig);
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("DROP USER %s CASCADE", schemaName)));
        });

    sshBastionContainer.stopAndCloseContainers(db);
  }

  @Override
  protected boolean supportsDBT() {
    return false;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

}
