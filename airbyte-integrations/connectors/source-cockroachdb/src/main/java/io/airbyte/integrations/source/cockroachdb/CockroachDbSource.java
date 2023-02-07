/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static io.airbyte.db.jdbc.JdbcUtils.AMPERSAND;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
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
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    final AirbyteConnectionStatus check = check(config);

    if (check.getStatus().equals(AirbyteConnectionStatus.Status.FAILED)) {
      throw new RuntimeException("Unable establish a connection: " + check.getMessage());
    }

    return super.read(config, catalog, state);
  }

  @Override
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
  protected DataSource createDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = toDatabaseConfig(config);

    final DataSource dataSource = DataSourceFactory.create(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClass,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        JdbcUtils.parseJdbcParameters(jdbcConfig, JdbcUtils.CONNECTION_PROPERTIES_KEY));
    dataSources.add(dataSource);
    return dataSource;
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode config) throws SQLException {
    final DataSource dataSource = createDataSource(config);
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource, sourceOperations);
    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    return new CockroachJdbcDatabase(database, sourceOperations);
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
