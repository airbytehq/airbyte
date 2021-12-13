/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.NoOpJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Collections;
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

  public static final List<String> SSL_PARAMETERS = List.of(
      "ssl=true",
      "sslmode=none");

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final JdbcDatabase database,
                                                          final List<TableInfo<CommonField<JDBCType>>> tableInfos) {
    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> sourceOperations
                .getFullyQualifiedTableName(tableInfo.getNameSpace(), tableInfo.getName()),
            tableInfo -> {
              try {
                return database.resultSetQuery(connection -> {
                  final String sql = "SELECT name FROM system.columns WHERE database = ? AND table = ? AND is_in_primary_key = 1";
                  final PreparedStatement preparedStatement = connection.prepareStatement(sql);
                  preparedStatement.setString(1, tableInfo.getNameSpace());
                  preparedStatement.setString(2, tableInfo.getName());
                  return preparedStatement.executeQuery();

                }, resultSet -> resultSet.getString("name")).collect(Collectors.toList());
              } catch (final SQLException e) {
                throw new RuntimeException(e);
              }
            }));
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseSource.class);
  public static final String DRIVER_CLASS = "ru.yandex.clickhouse.ClickHouseDriver";

  public static Source getWrappedSource() {
    return new SshWrappedSource(new ClickHouseSource(), List.of("host"), List.of("port"));
  }

  /**
   * The reason we use NoOpJdbcStreamingQueryConfiguration(not setting auto commit to false and not
   * setting fetch size to 1000) for ClickHouse is cause method
   * {@link ru.yandex.clickhouse.ClickHouseConnectionImpl#setAutoCommit} is empty and method
   * {@link ru.yandex.clickhouse.ClickHouseStatementImpl#setFetchSize} is empty
   */
  public ClickHouseSource() {
    super(DRIVER_CLASS, new NoOpJdbcStreamingQueryConfiguration(), JdbcUtils.getDefaultSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:clickhouse://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    // assume ssl if not explicitly mentioned.
    if (!config.has("ssl") || config.get("ssl").asBoolean()) {
      jdbcUrl.append("?").append(String.join("&", SSL_PARAMETERS));
    }

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("jdbc_url", jdbcUrl.toString())
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.singleton("system");
  }

  public static void main(final String[] args) throws Exception {
    final Source source = ClickHouseSource.getWrappedSource();
    LOGGER.info("starting source: {}", ClickHouseSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", ClickHouseSource.class);
  }

}
