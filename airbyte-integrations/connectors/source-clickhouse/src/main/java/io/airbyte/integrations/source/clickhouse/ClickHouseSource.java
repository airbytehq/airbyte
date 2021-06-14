/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickHouseSource extends AbstractJdbcSource implements Source {

  /**
   * The default implementation relies on {@link java.sql.DatabaseMetaData#getPrimaryKeys} method to
   * get it but the ClickHouse JDBC driver returns an empty result set from the method
   * {@link ru.yandex.clickhouse.ClickHouseDatabaseMetadata#getPrimaryKeys}. That's why we have to
   * query the system table mentioned here
   * https://clickhouse.tech/docs/en/operations/system-tables/columns/ to fetch the primary keys.
   */
  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(JdbcDatabase database,
                                                          Optional<String> databaseOptional,
                                                          List<TableInfoInternal> tableInfos) {

    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> JdbcUtils
                .getFullyQualifiedTableName(tableInfo.getSchemaName(), tableInfo.getName()),
            tableInfo -> {
              try {
                return database.resultSetQuery(connection -> {
                  String sql = "SELECT name FROM system.columns WHERE database = ? AND  table = ? AND is_in_primary_key = 1";
                  PreparedStatement preparedStatement = connection.prepareStatement(sql);
                  preparedStatement.setString(1, tableInfo.getSchemaName());
                  preparedStatement.setString(2, tableInfo.getName());
                  return preparedStatement.executeQuery();

                }, resultSet -> resultSet.getString("name")).collect(Collectors.toList());
              } catch (SQLException e) {
                throw new RuntimeException(e);
              }
            }));
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseSource.class);
  public static final String DRIVER_CLASS = "ru.yandex.clickhouse.ClickHouseDriver";

  /**
   * The reason we use NoOpJdbcStreamingQueryConfiguration(not setting auto commit to false and not
   * setting fetch size to 1000) for ClickHouse is cause method
   * {@link ru.yandex.clickhouse.ClickHouseConnectionImpl#setAutoCommit} is empty and method
   * {@link ru.yandex.clickhouse.ClickHouseStatementImpl#setFetchSize} is empty
   */
  public ClickHouseSource() {
    super(DRIVER_CLASS, new NoOpJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("jdbc_url", String.format("jdbc:clickhouse://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()))
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.singleton("system");
  }

  public static void main(String[] args) throws Exception {
    final Source source = new ClickHouseSource();
    LOGGER.info("starting source: {}", ClickHouseSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", ClickHouseSource.class);
  }

}
