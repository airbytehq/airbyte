/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc;

import static io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils.assertCustomParametersDontOverwriteDefaultParameters;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.sql.JDBCType;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Runs the acceptance tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
class DefaultJdbcSourceAcceptanceTest
    extends JdbcSourceAcceptanceTest<DefaultJdbcSourceAcceptanceTest.PostgresTestSource, DefaultJdbcSourceAcceptanceTest.BareBonesTestDatabase> {

  private static PostgreSQLContainer<?> PSQL_CONTAINER;

  @BeforeAll
  static void init() {
    PSQL_CONTAINER = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_CONTAINER.start();
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s BIT(3) NOT NULL);";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(B'101');";
  }

  @Override
  protected JsonNode config() {
    return testdb.testConfigBuilder().build();
  }

  @Override
  protected PostgresTestSource source() {
    return new PostgresTestSource();
  }

  @Override
  protected BareBonesTestDatabase createTestDatabase() {
    return new BareBonesTestDatabase(PSQL_CONTAINER).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  public JsonNode getConfigWithConnectionProperties(final PostgreSQLContainer<?> psqlDb, final String dbName, final String additionalParameters) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(psqlDb))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(psqlDb))
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, psqlDb.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, psqlDb.getPassword())
        .put(JdbcUtils.CONNECTION_PROPERTIES_KEY, additionalParameters)
        .build());
  }

  @AfterAll
  static void cleanUp() {
    PSQL_CONTAINER.close();
  }

  public static class PostgresTestSource extends AbstractJdbcSource<JDBCType> implements Source {

    private static final Logger LOGGER = LoggerFactory.getLogger(PostgresTestSource.class);

    static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

    public PostgresTestSource() {
      super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, JdbcUtils.getDefaultSourceOperations());
    }

    @Override
    public JsonNode toDatabaseConfig(final JsonNode config) {
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
          .put(JdbcUtils.JDBC_URL_KEY, String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
              config.get(JdbcUtils.HOST_KEY).asText(),
              config.get(JdbcUtils.PORT_KEY).asInt(),
              config.get(JdbcUtils.DATABASE_KEY).asText()));

      if (config.has(JdbcUtils.PASSWORD_KEY)) {
        configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
      }

      return Jsons.jsonNode(configBuilder.build());
    }

    @Override
    public Set<String> getExcludedInternalNameSpaces() {
      return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
    }

    @Override
    protected AirbyteStateType getSupportedStateType(final JsonNode config) {
      return AirbyteStateType.STREAM;
    }

    public static void main(final String[] args) throws Exception {
      final Source source = new PostgresTestSource();
      LOGGER.info("starting source: {}", PostgresTestSource.class);
      new IntegrationRunner(source).run(args);
      LOGGER.info("completed source: {}", PostgresTestSource.class);
    }

  }

  static protected class BareBonesTestDatabase
      extends TestDatabase<PostgreSQLContainer<?>, BareBonesTestDatabase, BareBonesTestDatabase.BareBonesConfigBuilder> {

    public BareBonesTestDatabase(PostgreSQLContainer<?> container) {
      super(container);
    }

    @Override
    protected Stream<Stream<String>> inContainerBootstrapCmd() {
      final var sql = Stream.of(
          String.format("CREATE DATABASE %s", getDatabaseName()),
          String.format("CREATE USER %s PASSWORD '%s'", getUserName(), getPassword()),
          String.format("GRANT ALL PRIVILEGES ON DATABASE %s TO %s", getDatabaseName(), getUserName()),
          String.format("ALTER USER %s WITH SUPERUSER", getUserName()));
      return Stream.of(Stream.concat(
          Stream.of("psql",
              "-d", getContainer().getDatabaseName(),
              "-U", getContainer().getUsername(),
              "-v", "ON_ERROR_STOP=1",
              "-a"),
          sql.flatMap(stmt -> Stream.of("-c", stmt))));
    }

    @Override
    protected Stream<String> inContainerUndoBootstrapCmd() {
      return Stream.empty();
    }

    @Override
    public DatabaseDriver getDatabaseDriver() {
      return DatabaseDriver.POSTGRESQL;
    }

    @Override
    public SQLDialect getSqlDialect() {
      return SQLDialect.POSTGRES;
    }

    @Override
    public BareBonesConfigBuilder configBuilder() {
      return new BareBonesConfigBuilder(this);
    }

    static protected class BareBonesConfigBuilder extends TestDatabase.ConfigBuilder<BareBonesTestDatabase, BareBonesConfigBuilder> {

      private BareBonesConfigBuilder(BareBonesTestDatabase testDatabase) {
        super(testDatabase);
      }

    }

  }

  @Test
  void testCustomParametersOverwriteDefaultParametersExpectException() {
    final String connectionPropertiesUrl = "ssl=false";
    final JsonNode config = getConfigWithConnectionProperties(PSQL_CONTAINER, testdb.getDatabaseName(), connectionPropertiesUrl);
    final Map<String, String> customParameters = JdbcUtils.parseJdbcParameters(config, JdbcUtils.CONNECTION_PROPERTIES_KEY, "&");
    final Map<String, String> defaultParameters = Map.of(
        "ssl", "true",
        "sslmode", "require");
    assertThrows(IllegalArgumentException.class, () -> {
      assertCustomParametersDontOverwriteDefaultParameters(customParameters, defaultParameters);
    });
  }

}
