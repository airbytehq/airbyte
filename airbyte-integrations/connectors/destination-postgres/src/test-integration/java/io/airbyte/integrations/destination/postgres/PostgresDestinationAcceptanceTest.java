/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

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
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private PostgreSQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
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

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    try (final DSLContext dslContext = DSLContextFactory.create(
        db.getUsername(),
        db.getPassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        db.getJdbcUrl(),
        SQLDialect.POSTGRES)) {
      return new Database(dslContext)
          .query(ctx -> {
            ctx.execute("set time zone 'UTC';");
            return ctx.fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
                .stream()
                .map(this::getJsonFromRecord)
                .collect(Collectors.toList());
          });
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    db = new PostgreSQLContainer<>("postgres:13-alpine");
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

}
