/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle_strict_encrypt;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.oracle.OracleNameTransformer;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.JSONFormat;
import org.junit.Test;

public class OracleStrictEncryptDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

  private final StandardNameTransformer namingResolver = new OracleNameTransformer();
  private static OracleContainer db;
  private static JsonNode config;
  private final String schemaName = "TEST_ORCL";

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle-strict-encrypt:dev";
  }

  private JsonNode getConfig(final OracleContainer db) {

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put("sid", db.getSid())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMAS_KEY, List.of("JDBC_SPACE"))
        .build());
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(
            r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
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
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = getConfig();
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
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

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {
    final String query =
        String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.toUpperCase());
    final DSLContext dslContext = getDslContext(config);
    final List<org.jooq.Record> result = getDatabase(dslContext).query(ctx -> ctx.fetch(query).stream().toList());
    return result
        .stream()
        .map(r -> r.formatJSON(JSON_FORMAT))
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get("sid").asText()),
        null);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);
    db = new OracleContainer()
        .withUsername("test")
        .withPassword("oracle")
        .usingSid();
    db.start();

    config = getConfig(db);
    final DSLContext dslContext = getDslContext(config);
    final Database database = getDatabase(dslContext);
    database.query(
        ctx -> ctx.fetch(String.format("CREATE USER %s IDENTIFIED BY %s", schemaName, schemaName)));
    database.query(ctx -> ctx.fetch(String.format("GRANT ALL PRIVILEGES TO %s", schemaName)));

    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, dbName);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Test
  public void testEncryption() throws SQLException {
    final String algorithm = "AES256";
    final JsonNode config = getConfig();
    final DataSource dataSource =
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get("sid").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED;" +
                "oracle.net.encryption_types_client=( " + algorithm + " )", ";"),
            Duration.ofMinutes(5));
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertThat(collect.get(2).get("NETWORK_SERVICE_BANNER").asText(),
        equals("Oracle Advanced Security: " + algorithm + " encryption"));
  }

  @Test
  public void testCheckProtocol() throws SQLException {
    final JsonNode clone = Jsons.clone(getConfig());

    final String algorithm = clone.get(JdbcUtils.ENCRYPTION_KEY)
        .get("encryption_algorithm").asText();

    final DataSource dataSource =
        DataSourceFactory.create(config.get(JdbcUtils.USERNAME_KEY).asText(), config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get("sid").asText()),
            JdbcUtils.parseJdbcParameters("oracle.net.encryption_client=REQUIRED;" +
                "oracle.net.encryption_types_client=( " + algorithm + " )", ";"),
            Duration.ofMinutes(5));
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    final String networkServiceBanner = "SELECT sys_context('USERENV', 'NETWORK_PROTOCOL') as network_protocol FROM dual";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertEquals("tcp", collect.get(0).get("NETWORK_PROTOCOL").asText());
  }

}
