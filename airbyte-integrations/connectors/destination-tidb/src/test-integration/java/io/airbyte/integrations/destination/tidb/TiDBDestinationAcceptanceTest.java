/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.integrations.util.HostPortResolver;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class TiDBDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new TiDBSQLNameTransformer();
  private GenericContainer container;
  private final String usernameKey = "root";
  private final String passwordKey = "";
  private final String databaseKey = "test";
  private final Boolean sslKey = false;

  @Override
  protected String getImageName() {
    return "airbyte/destination-tidb:dev";
  }


  @Override
  protected boolean implementsNamespaces() {
    return true;
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
  protected TestDataComparator getTestDataComparator() {
    return new TiDBTestDataComparator();
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.USERNAME_KEY, usernameKey)
        .put(JdbcUtils.DATABASE_KEY, databaseKey)
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.SSL_KEY, sslKey)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.USERNAME_KEY, usernameKey)
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.DATABASE_KEY, databaseKey)
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.SSL_KEY, sslKey)
        .build());
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
        usernameKey,
        passwordKey,
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            databaseKey),
        SQLDialect.MYSQL)) {
      return new Database(dslContext).query(
          ctx -> ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(this::getJsonFromRecord)
              .collect(Collectors.toList()));
    }
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    container = new GenericContainer(DockerImageName.parse("pingcap/tidb:nightly"))
        .withExposedPorts(4000);
    container.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    container.stop();
    container.close();
  }

}
