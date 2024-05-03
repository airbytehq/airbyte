/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Enable for V1
@Disabled
public class SingleStoreDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  public static final String DEFAULT_DEV_IMAGE = "airbyte/destination-singlestore:dev";

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreDestinationAcceptanceTest.class);

  private AirbyteSingleStoreTestContainer db;
  private final StandardNameTransformer namingResolver = new SingleStoreNameTransformer();

  @Override
  protected void setup(@NotNull DestinationAcceptanceTest.TestDestinationEnv testEnv, @NotNull HashSet<String> TEST_SCHEMAS) throws Exception {
    AirbyteSingleStoreTestContainer container = new AirbyteSingleStoreTestContainer();
    container.start();
    final String username = "user_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String password = RandomStringUtils.randomAlphabetic(10).toLowerCase();
    final String database = "database_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
    final String[] sql = new String[] {
      String.format("CREATE DATABASE %s", database),
      String.format("CREATE USER %s IDENTIFIED BY '%s'", username, password),
      String.format("GRANT ALL ON *.* TO %s", username)
    };
    container.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root", String.join("; ", sql)));
    db = container.withUsername(username).withPassword(password).withDatabaseName(database);
  }

  @NotNull
  @Override
  protected String getImageName() {
    return DEFAULT_DEV_IMAGE;
  }

  @NotNull
  @Override
  protected JsonNode getConfig() throws Exception {
    return Jsons.jsonNode(ImmutableMap.builder().put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db)).put(JdbcUtils.USERNAME_KEY,
        db.getUsername()).put(JdbcUtils.PASSWORD_KEY, db.getPassword()).put(JdbcUtils.DATABASE_KEY, db.getDatabaseName()).put(JdbcUtils.PORT_KEY,
            HostPortResolver.resolvePort(db))
        .put(JdbcUtils.SSL_KEY, false).build());
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Nullable
  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final ObjectNode config = (ObjectNode) getConfig();
    config.put(JdbcUtils.PASSWORD_KEY, "wrong password");
    return config;
  }

  @NotNull
  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           @NotNull final String streamName,
                                           @NotNull final String namespace,
                                           @NotNull final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace).stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA)).collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final DSLContext dslContext = DSLContextFactory.create(db.getUsername(), db.getPassword(), db.getDriverClassName(),
        String.format("jdbc:singlestore://%s:%s/%s", db.getHost(), db.getFirstMappedPort(), db.getDatabaseName()), SQLDialect.DEFAULT);
    return new Database(dslContext).query(
        ctx -> ctx.fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .stream().map(this::getJsonFromRecord).collect(Collectors.toList()));
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
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected void tearDown(@NotNull DestinationAcceptanceTest.TestDestinationEnv testEnv) throws Exception {
    db.stop();
    db.close();
  }

}
