/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.assertCustomParametersDontOverwriteDefaultParameters;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.JDBCType;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

/**
 * Runs the acceptance tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
class DefaultJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static PostgreSQLContainer<?> PSQL_DB;

  private JsonNode config;
  private String dbName;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s BIT(3) NOT NULL);";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(B'101');";
  }

  @BeforeEach
  public void setup() throws Exception {
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, PSQL_DB.getHost())
        .put(JdbcUtils.PORT_KEY, PSQL_DB.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, PSQL_DB.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, PSQL_DB.getPassword())
        .build());

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    super.setup();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new PostgresTestSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
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

  @Override
  public String getDriverClass() {
    return PostgresTestSource.DRIVER_CLASS;
  }

  @Override
  protected boolean supportsPerStream() {
    return true;
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  private static class PostgresTestSource extends AbstractJdbcSource<JDBCType> implements Source {

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

    // TODO This is a temporary override so that the Postgres source can take advantage of per-stream
    // state
    @Override
    protected List<AirbyteStateMessage> generateEmptyInitialState(final JsonNode config) {
      if (getSupportedStateType(config) == AirbyteStateType.GLOBAL) {
        final AirbyteGlobalState globalState = new AirbyteGlobalState()
            .withSharedState(Jsons.jsonNode(new CdcState()))
            .withStreamStates(List.of());
        return List.of(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState));
      } else {
        return List.of(new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()));
      }
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

  @Test
  void testCustomParametersOverwriteDefaultParametersExpectException() {
    final String connectionPropertiesUrl = "ssl=false";
    final JsonNode config = getConfigWithConnectionProperties(PSQL_DB, dbName, connectionPropertiesUrl);
    final Map<String, String> customParameters = JdbcUtils.parseJdbcParameters(config, JdbcUtils.CONNECTION_PROPERTIES_KEY, "&");
    final Map<String, String> defaultParameters = Map.of(
        "ssl", "true",
        "sslmode", "require");
    assertThrows(IllegalArgumentException.class, () -> {
      assertCustomParametersDontOverwriteDefaultParameters(customParameters, defaultParameters);
    });
  }

}
