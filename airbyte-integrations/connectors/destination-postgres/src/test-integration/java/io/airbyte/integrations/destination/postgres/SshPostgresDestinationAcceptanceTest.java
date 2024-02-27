/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.cdk.integrations.base.ssh.SshTunnel.CONNECTION_OPTIONS_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.ContainerModifier;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.SQLDialect;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshPostgresDestinationAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testdb;
  private SshBastionContainer bastion;

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected JsonNode getConfig() throws Exception {
    // Here we use inner address because the tunnel is created inside the connector's container.
    return testdb.integrationTestConfigBuilder()
        .with("tunnel_method", bastion.getTunnelMethod(getTunnelMethod(), true))
        .with("schema", "public")
        .withoutSsl()
        .build();
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return new Database(
        DSLContextFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()),
            SQLDialect.POSTGRES));
  }

  @Override
  protected List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    // Here we DO NOT use the inner address because the tunnel is created in the integration test's java
    // process.
    final JsonNode config = testdb.integrationTestConfigBuilder()
        .with("tunnel_method", bastion.getTunnelMethod(getTunnelMethod(), false))
        .with("schema", "public")
        .withoutSsl()
        .build();
    ((ObjectNode) config).putObject(CONNECTION_OPTIONS_KEY);
    return SshTunnel.sshWrap(
        config,
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
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
  protected void setup(final TestDestinationEnv testEnv, HashSet<String> TEST_SCHEMAS) throws Exception {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_13, ContainerModifier.NETWORK);
    bastion = new SshBastionContainer();
    bastion.initAndStartBastion(testdb.getContainer().getNetwork());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    testdb.close();
    bastion.stopAndClose();
  }

  @Override
  protected PostgresTestDatabase getTestDb() {
    return testdb;
  }

}
