/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;

import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

@Disabled
public abstract class SshOceanBaseDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private final StandardNameTransformer namingResolver = new OceanBaseNameTransformer();
  private String schemaName;

  private final SshBastionContainer sshBastionContainer = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private OceanBaseContainer db;

  @Override
  protected @NotNull JsonNode getConfig() throws IOException, InterruptedException {
    return Objects.requireNonNull(sshBastionContainer.getTunnelConfig(getTunnelMethod(),
            getConfigFromTestContainer(db).put(JdbcUtils.SCHEMA_KEY, schemaName), false));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-oceanbase:dev";
  }

  public static ImmutableMap.Builder<Object, Object> getConfigFromTestContainer(final OceanBaseContainer db) {
    return ImmutableMap.builder()
            .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
            .put(JdbcUtils.USERNAME_KEY, db.getUsername())
            .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
            .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
            .put(JdbcUtils.SCHEMA_KEY, db.getDatabaseName())
            .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
            .put(JdbcUtils.SSL_KEY, false);
  }

  @Override
  protected JsonNode getFailCheckConfig() throws IOException, InterruptedException {
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
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new OceanBaseTestDataComparator();
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    final var tableName = namingResolver.getIdentifier(streamName);
    final String schema = namespace != null ? namingResolver.getIdentifier(namespace) : namingResolver.getIdentifier(schemaName);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        OceanBaseDestination.DRIVER_CLASS,
        String.format(OceanBaseDestination.URL_FORMAT_STRING,
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asText(),
            config.get(JdbcUtils.SCHEMA_KEY)),
        SQLDialect.MYSQL);
    return new Database(dslContext);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final var schema = schemaName == null ? this.schemaName : schemaName;
    return SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schema, tableName.toLowerCase(),
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(this::getJsonFromRecord)
                    .collect(Collectors.toList())));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
    final var config = getConfig();
    SshTunnel.sshWrap(
        config,
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("CREATE DATABASE %s;", schemaName)));
        });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("DROP DATABASE %s", schemaName)));
        });
  }

}
