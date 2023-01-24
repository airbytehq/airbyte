/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.NoOpStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickHouseSource extends AbstractJdbcSource<JDBCType> implements Source {

  /**
   * The default implementation relies on {@link java.sql.DatabaseMetaData#getPrimaryKeys} method to
   * get it but the ClickHouse JDBC driver returns an empty result set from the method
   * {@link ru.yandex.clickhouse.ClickHouseDatabaseMetadata#getPrimaryKeys}. That's why we have to
   * query the system table mentioned here
   * https://clickhouse.tech/docs/en/operations/system-tables/columns/ to fetch the primary keys.
   */

  public static final String SSL_MODE = "sslmode=none";
  public static final String HTTPS_PROTOCOL = "https";
  public static final String HTTP_PROTOCOL = "http";

  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final JdbcDatabase database,
                                                          final List<TableInfo<CommonField<JDBCType>>> tableInfos) {
    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> JdbcUtils.getFullyQualifiedTableName(tableInfo.getNameSpace(), tableInfo.getName()),
            tableInfo -> {
              try {
                return database.queryStrings(connection -> {
                  final String sql = "SELECT name FROM system.columns WHERE database = ? AND table = ? AND is_in_primary_key = 1";
                  final PreparedStatement preparedStatement = connection.prepareStatement(sql);
                  preparedStatement.setString(1, tableInfo.getNameSpace());
                  preparedStatement.setString(2, tableInfo.getName());
                  return preparedStatement.executeQuery();
                }, resultSet -> resultSet.getString("name"));
              } catch (final SQLException e) {
                throw new RuntimeException(e);
              }
            }));
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseSource.class);
  public static final String DRIVER_CLASS = DatabaseDriver.CLICKHOUSE.getDriverClassName();

  public static Source getWrappedSource() {
    return new SshWrappedSource(new ClickHouseSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  /**
   * The reason we use NoOpStreamingQueryConfig(not setting auto commit to false and not setting fetch
   * size to 1000) for ClickHouse is cause method
   * {@link ru.yandex.clickhouse.ClickHouseConnectionImpl#setAutoCommit} is empty and method
   * {@link ru.yandex.clickhouse.ClickHouseStatementImpl#setFetchSize} is empty
   */
  public ClickHouseSource() {
    super(DRIVER_CLASS, NoOpStreamingQueryConfig::new, JdbcUtils.getDefaultSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final boolean isSsl = !config.has("ssl") || config.get("ssl").asBoolean();
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:clickhouse:%s://%s:%s/%s",
        isSsl ? HTTPS_PROTOCOL : HTTP_PROTOCOL,
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    final boolean isAdditionalParamsExists =
        config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty();
    final List<String> params = new ArrayList<>();
    // assume ssl if not explicitly mentioned.
    if (isSsl) {
      params.add(SSL_MODE);
    }
    if (isAdditionalParamsExists) {
      params.add(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    if (isSsl || isAdditionalParamsExists) {
      jdbcUrl.append("?");
      jdbcUrl.append(String.join("&", params));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("system", "information_schema", "INFORMATION_SCHEMA");
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = ClickHouseSource.getWrappedSource();
    LOGGER.info("starting source: {}", ClickHouseSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", ClickHouseSource.class);
  }

}
