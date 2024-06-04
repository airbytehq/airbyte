/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 * <p>
 * This class probably should extend {@link MySQLDestinationAcceptanceTest} to further reduce code
 * duplication though.
 */
@Disabled
public abstract class SshMySQLDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private final StandardNameTransformer namingResolver = new MySQLNameTransformer();
  private String schemaName;

  public abstract Path getConfigFilePath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final var config = getConfigFromSecretsFile();
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, schemaName);
    return config;
  }

  private JsonNode getConfigFromSecretsFile() {
    return Jsons.deserialize(IOs.readFile(getConfigFilePath()));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
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
    return new MySqlTestDataComparator();
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
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asText()),
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

  /**
   * Disabled for the same reason as in {@link MySQLDestinationAcceptanceTest}. But for some reason,
   * this class doesn't extend that one so we have to do it again.
   */
  @Override
  @Disabled("MySQL normalization uses the wrong datatype for numbers. This will not be fixed, because we intend to replace normalization with DV2.")
  public void testDataTypeTestWithNormalization(final String messagesFilename,
                                                final String catalogFilename,
                                                final DataTypeTestArgumentProvider.TestCompatibility testCompatibility)
      throws Exception {
    super.testDataTypeTestWithNormalization(messagesFilename, catalogFilename, testCompatibility);
  }

}
