/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;

// todo (cgardens) - likely some of this could be further de-duplicated with
// PostgresDestinationAcceptanceTest.

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshPostgresDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();
  private static final String schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
  private static PostgreSQLContainer<?> db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db).put("schema", schemaName));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
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
  protected boolean supportsNormalization() {
    return true;
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
  protected TestDataComparator getTestDataComparator() {
    return new PostgresTestDataComparator();
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return new Database(
        DSLContextFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("database").asText()),
            SQLDialect.POSTGRES
        )
    );
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final JsonNode config = getConfig();
    return SshTunnel.sshWrap(
        config,
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(ctx -> {
              ctx.execute("set time zone 'UTC';");
              return ctx.fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                  .stream()
                  .map(this::getJsonFromRecord)
                  .collect(Collectors.toList());
            }));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {

    startTestContainers();
    // do everything in a randomly generated schema so that we can wipe it out at the end.
    SshTunnel.sshWrap(
        getConfig(),
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("CREATE SCHEMA %s;", schemaName)));
        });
  }

  private void startTestContainers() {
    bastion.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new PostgreSQLContainer<>("postgres:13-alpine")
        .withNetwork(bastion.getNetWork());
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    // blow away the test schema at the end.
    SshTunnel.sshWrap(
        getConfig(),
        PostgresDestination.HOST_KEY,
        PostgresDestination.PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("DROP SCHEMA %s CASCADE;", schemaName)));
        });

    bastion.stopAndCloseContainers(db);
  }

}
