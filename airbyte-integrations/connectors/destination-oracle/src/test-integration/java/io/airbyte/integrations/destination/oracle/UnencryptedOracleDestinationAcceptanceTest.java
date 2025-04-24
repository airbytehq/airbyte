/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static io.airbyte.cdk.integrations.base.JavaBaseConstantsKt.upperQuoted;
import static io.airbyte.cdk.integrations.util.HostPortResolver.resolveHost;
import static io.airbyte.cdk.integrations.util.HostPortResolver.resolvePort;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;

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
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.junit.jupiter.api.Test;

public class UnencryptedOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final StandardNameTransformer namingResolver = new OracleNameTransformer();
  private static OracleContainer db;
  private static JsonNode config;
  private final String schemaName = "TEST_ORCL";

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle:dev";
  }

  private JsonNode getConfig(final OracleContainer db) {

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, resolveHost(db))
        .put(JdbcUtils.PORT_KEY, resolvePort(db))
        .put("sid", db.getSid())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMAS_KEY, List.of("JDBC_SPACE"))
        .put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()))
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
    return retrieveRecordsFromTable(namingResolver.convertStreamName(StreamId.concatenateRawTableName(namespace, streamName)), namespace)
        .stream()
        .map(r -> Jsons.deserialize(
            r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase()).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new OracleTestDataComparator();
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
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = getConfig();
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {
    final DSLContext dslContext = getDSLContext(config);
    final List<org.jooq.Record> result = getDatabase(dslContext)
        .query(ctx -> new ArrayList<>(ctx.fetch(
            String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName,
                upperQuoted(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)))));
    return result
        .stream()
        .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  private static DSLContext getDSLContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(), config.get(JdbcUtils.PASSWORD_KEY).asText(), DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get("sid").asText()),
        null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, HashSet<String> TEST_SCHEMAS) throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);
    db = new OracleContainer()
        .withUsername("test")
        .withPassword("oracle")
        .usingSid();
    db.start();

    config = getConfig(db);
    final DSLContext dslContext = getDSLContext(config);
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
  public void testNoneEncryption() throws SQLException {
    final JsonNode config = getConfig();

    final DataSource dataSource =
        DataSourceFactory.create(config.get(JdbcUtils.USERNAME_KEY).asText(), config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get("sid").asText()));
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertThat(collect.get(1).get("NETWORK_SERVICE_BANNER").asText(),
        is(equalTo("Encryption service for Linux: Version 18.0.0.0.0 - Production")));
  }

}
