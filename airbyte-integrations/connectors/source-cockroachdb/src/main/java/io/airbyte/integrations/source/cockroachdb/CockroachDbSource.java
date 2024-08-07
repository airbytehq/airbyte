/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.AMPERSAND;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CockroachDbSource extends AbstractJdbcSource<JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CockroachDbSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

  public CockroachDbSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new CockroachJdbcSourceOperations());
  }

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new CockroachDbSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {

    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText()).append(AMPERSAND);
    }

    if (config.has(JdbcUtils.SSL_KEY) && config.get(JdbcUtils.SSL_KEY).asBoolean() || !config.has(JdbcUtils.SSL_KEY)) {
      additionalParameters.add("ssl=true");
      additionalParameters.add("sslmode=require");
    }

    additionalParameters.forEach(x -> jdbcUrl.append(x).append("&"));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    LOGGER.warn(jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set
        .of("information_schema", "pg_catalog", "pg_internal", "catalog_history", "pg_extension",
            "crdb_internal");
  }

  @Override
  @SuppressWarnings("unchecked")
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    try (final Stream<JsonNode> stream = database.unsafeQuery(getPrivileges(database), sourceOperations::rowToJson)) {
      return stream.map(this::getPrivilegeDto).collect(Collectors.toSet());
    }
  }

  @Override
  protected boolean isNotInternalSchema(final JsonNode jsonNode, final Set<String> internalSchemas) {
    return false;
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    final Map<String, String> connectionProperties = JdbcUtils.parseJdbcParameters(jdbcConfig, JdbcUtils.CONNECTION_PROPERTIES_KEY);
    // Create the JDBC data source
    final DataSource dataSource = DataSourceFactory.create(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClassName,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        connectionProperties,
        getConnectionTimeout(connectionProperties, driverClassName));
    dataSources.add(dataSource);

    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource, sourceOperations);
    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    final CockroachJdbcDatabase cockroachJdbcDatabase = new CockroachJdbcDatabase(database, sourceOperations);
    cockroachJdbcDatabase.setSourceConfig(sourceConfig);
    cockroachJdbcDatabase.setDatabaseConfig(toDatabaseConfig(sourceConfig));
    return cockroachJdbcDatabase;
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  private CheckedFunction<Connection, PreparedStatement, SQLException> getPrivileges(final JdbcDatabase database) {
    return connection -> {
      final PreparedStatement ps = connection.prepareStatement(
          "SELECT DISTINCT table_catalog, table_schema, table_name, privilege_type\n"
              + "FROM   information_schema.table_privileges\n"
              + "WHERE  (grantee  = ? AND privilege_type in ('SELECT', 'ALL')) OR (table_schema = 'public')");
      ps.setString(1, database.getDatabaseConfig().get(JdbcUtils.USERNAME_KEY).asText());
      return ps;
    };
  }

  private JdbcPrivilegeDto getPrivilegeDto(final JsonNode jsonNode) {
    return JdbcPrivilegeDto.builder()
        .schemaName(jsonNode.get("table_schema").asText())
        .tableName(jsonNode.get("table_name").asText())
        .build();
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new CockroachDbSource();
    LOGGER.info("starting source: {}", CockroachDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", CockroachDbSource.class);
  }

}
