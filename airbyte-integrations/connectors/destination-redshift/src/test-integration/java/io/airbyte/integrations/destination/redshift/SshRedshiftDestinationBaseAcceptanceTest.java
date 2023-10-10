/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_KEY_AUTH;
import static io.airbyte.cdk.integrations.base.ssh.SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.ConnectionFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import java.io.IOException;
import java.sql.Connection;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.jooq.impl.DSL;

public abstract class SshRedshiftDestinationBaseAcceptanceTest extends JdbcDestinationAcceptanceTest {

  protected String schemaName;
  // config from which to create / delete schemas.
  protected JsonNode baseConfig;
  // config which refers to the schema that the test is being run in.
  protected JsonNode config;

  private Database database;

  private Connection connection;

  private final RedshiftSQLNameTransformer namingResolver = new RedshiftSQLNameTransformer();
  private final String USER_WITHOUT_CREDS = Strings.addRandomSuffix("test_user", "_", 5);

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    final Map<Object, Object> configAsMap = deserializeToObjectMap(config);
    final Builder<Object, Object> configMapBuilder = new Builder<>().putAll(configAsMap);
    return getTunnelConfig(getTunnelMethod(), configMapBuilder);
  }

  protected JsonNode getTunnelConfig(final SshTunnel.TunnelMethod tunnelMethod, final ImmutableMap.Builder<Object, Object> builderWithSchema) {
    final JsonNode sshBastionHost = config.get("ssh_bastion_host");
    final JsonNode sshBastionPort = config.get("ssh_bastion_port");
    final JsonNode sshBastionUser = config.get("ssh_bastion_user");
    final JsonNode sshBastionPassword = config.get("ssh_bastion_password");
    final JsonNode sshBastionKey = config.get("ssh_bastion_key");

    final String tunnelUserPassword = tunnelMethod.equals(SSH_PASSWORD_AUTH) ? sshBastionPassword.asText() : "";
    final String sshKey = tunnelMethod.equals(SSH_KEY_AUTH) ? sshBastionKey.asText() : "";

    return Jsons.jsonNode(builderWithSchema
        .put("tunnel_method", Jsons.jsonNode(ImmutableMap.builder()
            .put("tunnel_host", sshBastionHost)
            .put("tunnel_method", tunnelMethod.toString())
            .put("tunnel_port", sshBastionPort.intValue())
            .put("tunnel_user", sshBastionUser)
            .put("tunnel_user_password", tunnelUserPassword)
            .put("ssh_key", sshKey)
            .build()))
        .build());
  }

  public static Map<Object, Object> deserializeToObjectMap(final JsonNode json) {
    final ObjectMapper objectMapper = MoreMappers.initMapper();
    return objectMapper.convertValue(json, new TypeReference<>() {});
  }

  public abstract JsonNode getStaticConfig() throws IOException;

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(j -> j.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    return SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        config -> {
          return getDatabase().query(ctx -> ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(this::getJsonFromRecord)
              .collect(Collectors.toList()));
        });

  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new RedshiftTestDataComparator();
  }

  private Database createDatabaseFromConfig(final JsonNode config) {
    connection = ConnectionFactory.create(config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        RedshiftInsertDestination.SSL_JDBC_PARAMETERS,
        String.format(DatabaseDriver.REDSHIFT.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    return new Database(DSL.using(connection));
  }

  private Database getDatabase() {
    return database;
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    baseConfig = getStaticConfig();
    final JsonNode configForSchema = Jsons.clone(baseConfig);
    schemaName = TestingNamespaces.generate();
    TEST_SCHEMAS.add(schemaName);
    ((ObjectNode) configForSchema).put("schema", schemaName);
    config = configForSchema;
    database = createDatabaseFromConfig(config);
    // create the schema

    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        config -> {
          getDatabase().query(ctx -> ctx.fetch(String.format("CREATE SCHEMA %s;", schemaName)));
        });

    // create the user
    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        config -> {
          getDatabase().query(ctx -> ctx.fetch(String.format("CREATE USER %s WITH PASSWORD '%s' SESSION TIMEOUT 60;",
              USER_WITHOUT_CREDS, baseConfig.get("password").asText())));
        });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    // blow away the test schema at the end.
    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        config -> {
          getDatabase().query(ctx -> ctx.fetch(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", schemaName)));
        });

    // blow away the user at the end.
    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        config -> {
          getDatabase().query(ctx -> ctx.fetch(String.format("DROP USER IF EXISTS %s;", USER_WITHOUT_CREDS)));
        });
    RedshiftConnectionHandler.close(connection);
  }

}
