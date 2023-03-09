/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
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
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshMSSQLDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private final String schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
  private static final String database = "test";
  private static MSSQLServerContainer<?> db;
  private static final Network network = Network.newNetwork();
  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mssql:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db, database).put(JdbcUtils.SCHEMA_KEY, schemaName));
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
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%s",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        null);
    return new Database(dslContext);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final var schema = schemaName == null ? this.schemaName : schemaName;
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("USE %s;"
                        + "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        database, schema, tableName.toLowerCase(),
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(this::getJsonFromRecord)
                    .collect(Collectors.toList())));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    startTestContainers();

    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
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
    bastion.initAndStartBastion(network);
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-CU16-ubuntu-20.04")
        .withNetwork(network)
        .acceptLicense()
        .dependsOn(bastion.getContainer());
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new MSSQLTestDataComparator();
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

}
