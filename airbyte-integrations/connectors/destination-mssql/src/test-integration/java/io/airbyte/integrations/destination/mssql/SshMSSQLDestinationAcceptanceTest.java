/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshMSSQLDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private final String schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
  private static final String database = "test";
  private static MSSQLServerContainer<?> db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mssql:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), getMSSQLDbConfigBuilder(db));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
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

  public ImmutableMap.Builder<Object, Object> getMSSQLDbConfigBuilder(final JdbcDatabaseContainer<?> db) {
    return ImmutableMap.builder()
        .put("host", Objects.requireNonNull(db.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .get(((Network.NetworkImpl) bastion.getNetWork()).getName())
            .getIpAddress()))
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("port", db.getExposedPorts().get(0))
        .put("database", database)
        .put("schema", schemaName)
        .put("ssl", false);
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s",
            config.get("host").asText(),
            config.get("port").asInt()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final var schema = schemaName == null ? this.schemaName : schemaName;
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        MSSQLDestination.HOST_KEY,
        MSSQLDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("USE %s;"
                        + "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        database, schema, tableName.toLowerCase(),
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                    .map(Jsons::deserialize)
                    .collect(Collectors.toList())));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    startTestContainers();

    SshTunnel.sshWrap(
        getConfig(),
        MSSQLDestination.HOST_KEY,
        MSSQLDestination.PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> {
            ctx.fetch(String.format("CREATE DATABASE %s;", database));
            ctx.fetch(String.format("USE %s;", database));
            ctx.fetch(String.format("CREATE SCHEMA %s;", schemaName));

            return null;
          });
        });
  }

  private void startTestContainers() {
    bastion.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-GA-ubuntu-16.04")
        .withNetwork(bastion.getNetWork())
        .acceptLicense();
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

}
