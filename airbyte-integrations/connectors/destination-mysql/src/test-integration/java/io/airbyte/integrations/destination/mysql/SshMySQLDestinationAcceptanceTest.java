/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshMySQLDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new MySQLNameTransformer();
  private final List<String> HOST_KEY = List.of(MySQLDestination.HOST_KEY);
  private final List<String> PORT_KEY = List.of(MySQLDestination.PORT_KEY);
  private String schemaName;

  public abstract Path getConfigFilePath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final var config = getConfigFromSecretsFile();
    ((ObjectNode) config).put("database", schemaName);
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
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    final var tableName = namingResolver.getIdentifier(streamName);
    final String schema = namespace != null ? namingResolver.getIdentifier(namespace) : namingResolver.getIdentifier(schemaName);
    return retrieveRecordsFromTable(tableName, schema);
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

  private static Database getDatabaseFromConfig(final JsonNode config) {
    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        "com.mysql.cj.jdbc.Driver",
        String.format("jdbc:mysql://%s:%s",
            config.get("host").asText(),
            config.get("port").asText()), SQLDialect.MYSQL);
    return new Database(dslContext);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    final var schema = schemaName == null ? this.schemaName : schemaName;
    return SshTunnel.sshWrap(
        getConfig(),
        HOST_KEY,
        PORT_KEY,
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(
                ctx -> ctx
                    .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schema, tableName.toLowerCase(),
                        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                    .stream()
                    .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
                    .map(Jsons::deserialize)
                    .collect(Collectors.toList())));
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    schemaName = RandomStringUtils.randomAlphabetic(8).toLowerCase();
    final var config = getConfig();
    SshTunnel.sshWrap(
        config,
        HOST_KEY,
        PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("CREATE DATABASE %s;", schemaName)));
        });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    SshTunnel.sshWrap(
        getConfig(),
        HOST_KEY,
        PORT_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("DROP DATABASE %s", schemaName)));
        });
  }

  protected void assertSameValue(final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue.isBoolean()) {
      // Boolean in MySQL are stored as TINYINT (0 or 1) so we force them to boolean values here
      assertEquals(expectedValue.asBoolean(), actualValue.asBoolean());
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

}
