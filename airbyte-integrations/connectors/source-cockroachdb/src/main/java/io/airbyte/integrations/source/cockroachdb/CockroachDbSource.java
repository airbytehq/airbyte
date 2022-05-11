/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

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
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CockroachDbSource extends AbstractJdbcSource<JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CockroachDbSource.class);

  static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public CockroachDbSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new CockroachJdbcSourceOperations());
  }

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new CockroachDbSource(), HOST_KEY, PORT_KEY);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {

    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:postgresql://%s:%s/%s?",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    if (config.has("ssl") && config.get("ssl").asBoolean() || !config.has("ssl")) {
      additionalParameters.add("ssl=true");
      additionalParameters.add("sslmode=require");
    }

    additionalParameters.forEach(x -> jdbcUrl.append(x).append("&"));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    LOGGER.warn(jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
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
  public JdbcDatabase createDatabase(final JsonNode config) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(config);

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            jdbcConfig.get("username").asText(),
            jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
            driverClass,
            jdbcConfig.get("jdbc_url").asText(),
            JdbcUtils.parseJdbcParameters(jdbcConfig, "connection_properties")
        ),
        sourceOperations
    );

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);

    return new CockroachJdbcDatabase(database, sourceOperations);
  }

  private CheckedFunction<Connection, PreparedStatement, SQLException> getPrivileges(final JdbcDatabase database) {
    return connection -> {
      final PreparedStatement ps = connection.prepareStatement(
          "SELECT DISTINCT table_catalog, table_schema, table_name, privilege_type\n"
              + "FROM   information_schema.table_privileges\n"
              + "WHERE  (grantee  = ? AND privilege_type in ('SELECT', 'ALL')) OR (table_schema = 'public')");
      ps.setString(1, database.getDatabaseConfig().get("username").asText());
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
