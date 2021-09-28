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
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.jooq.JSONFormat;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.OracleContainer;

public abstract class SshOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

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
    return sshBastionContainer.getTunnelConfig(getTunnelMethod(), getBasicOracleDbConfigBuider(db).put("schema", schemaName));
  }

  public ImmutableMap.Builder<Object, Object> getBasicOracleDbConfigBuider(OracleContainer db) {
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
        .put("ssl", false);
  }

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName, String namespace, JsonNode streamSchema) throws Exception {
    List<JsonNode> jsonNodes = retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace);
    return jsonNodes
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase()).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv env, String streamName, String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
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
            .map(r -> r.formatJSON(JSON_FORMAT))
            .map(Jsons::deserialize)
            .collect(Collectors.toList()));
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    startTestContainers();
    SshTunnel.sshWrap(
        getConfig(),
        OracleDestination.HOST_KEY,
        OracleDestination.PORT_KEY,
        mangledConfig -> {
          Database databaseFromConfig = getDatabaseFromConfig(mangledConfig);
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("CREATE USER %s IDENTIFIED BY %s", schemaName, schemaName)));
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("GRANT ALL PRIVILEGES TO %s", schemaName)));
        });
  }

  private void startTestContainers() {
    sshBastionContainer.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new OracleContainer("epiclabs/docker-oracle-xe-11g")
        .withNetwork(sshBastionContainer.getNetWork());
    db.start();
  }

  private Database getDatabaseFromConfig(final JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:oracle:thin:@//%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("sid").asText()),
        "oracle.jdbc.driver.OracleDriver",
        null);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    SshTunnel.sshWrap(
        getConfig(),
        OracleDestination.HOST_KEY,
        OracleDestination.PORT_KEY,
        mangledConfig -> {
          Database databaseFromConfig = getDatabaseFromConfig(mangledConfig);
          databaseFromConfig.query(ctx -> ctx.fetch(String.format("DROP USER %s CASCADE", schemaName)));
        });

    sshBastionContainer.stopAndCloseContainers(db);
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

}
