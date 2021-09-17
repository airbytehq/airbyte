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

package io.airbyte.integrations.source.druid;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.NoOpJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.SourceJdbcUtils;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import org.apache.commons.dbcp2.BasicDataSource;
import java.io.FileWriter;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DruidSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(DruidSource.class);
  public static final String DRIVER_CLASS = "org.apache.calcite.jdbc.Driver";
  private static final String MODEL_FILE = "druid-model.json";

  private static final String JDBC_COLUMN_DATABASE_NAME = "TABLE_CAT";
  private static final String JDBC_COLUMN_SCHEMA_NAME = "TABLE_SCHEM";
  private static final String JDBC_COLUMN_TABLE_NAME = "TABLE_NAME";
  private static final String JDBC_COLUMN_COLUMN_NAME = "COLUMN_NAME";
  private static final String JDBC_COLUMN_DATA_TYPE = "DATA_TYPE";
  private static final String JDBC_COLUMN_DATA_TYPE_NAME = "TYPE_NAME";

  private static final String INTERNAL_SCHEMA_NAME = "schemaName";
  private static final String INTERNAL_TABLE_NAME = "tableName";
  private static final String INTERNAL_COLUMN_NAME = "columnName";
  private static final String INTERNAL_COLUMN_TYPE = "columnType";
  private static final String INTERNAL_COLUMN_TYPE_NAME = "columnTypeName";


  public DruidSource() {
    super(DRIVER_CLASS, new NoOpJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    String model = config.get("model").asText();
    FileWriter modelFile = null;
    try {
      modelFile = new FileWriter(MODEL_FILE);
      modelFile.write(model);
      modelFile.close();
    } catch (Exception e) {
      LOGGER.warn("Could not write model file \n");
    } finally {
      LOGGER.info("Created model file \n");
    }
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("jdbc_url", "jdbc:calcite:model="+MODEL_FILE)
        .build());
  }

  @Override
  protected String getQuoteString() {
    return "\"";
  }

  @Override
  public JdbcDatabase createDatabase(JsonNode config) throws SQLException {
    JsonNode jdbcConfig = toDatabaseConfig(config);

    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDefaultReadOnly(true);
    connectionPool.setDriverClassName(DRIVER_CLASS);
    connectionPool.setUsername(jdbcConfig.get("username").asText());
    connectionPool.setPassword(jdbcConfig.get("password").asText());
    connectionPool.setUrl(jdbcConfig.get("jdbc_url").asText());
    return new DefaultJdbcDatabase(connectionPool);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.singleton("system");
  }

  @Override
  protected List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database, String schema) throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalNameSpaces());
    return database.bufferedResultSetQuery(
        conn -> conn.getMetaData().getColumns(null, schema, null, null),
        resultSet -> Jsons.jsonNode(ImmutableMap.<String, Object>builder()
            // we always want a namespace, if we cannot get a schema, use db name.
            .put(INTERNAL_SCHEMA_NAME,
                resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                    : resultSet.getObject(JDBC_COLUMN_DATABASE_NAME))
            .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME))
            .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME))
            .put(INTERNAL_COLUMN_TYPE, resultSet.getString(JDBC_COLUMN_DATA_TYPE))
            .put(INTERNAL_COLUMN_TYPE_NAME, resultSet.getString(JDBC_COLUMN_DATA_TYPE_NAME))
            .build()))
        .stream()
        .filter(t -> !internalSchemas.contains(t.get(INTERNAL_SCHEMA_NAME).asText()))
        // group by schema and table name to handle the case where a table with the same name exists in
        // multiple schemas.
        .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
        .values()
        .stream()
        .map(fields -> TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(fields.get(0).get(INTERNAL_SCHEMA_NAME).asText())
            .name(fields.get(0).get(INTERNAL_TABLE_NAME).asText())
            .fields(fields.stream()
                .map(f -> {
                  JDBCType jdbcType;
                  try {
                    if ((f.get(INTERNAL_COLUMN_TYPE).asInt() == 1111) && 
                        (f.get(INTERNAL_COLUMN_TYPE_NAME).asText().equals("TIMESTAMP_WITH_LOCAL_TIME_ZONE(0) NOT NULL"))) {
                       jdbcType = JDBCType.valueOf("BIGINT");
		    } else {
                       jdbcType = JDBCType.valueOf(f.get(INTERNAL_COLUMN_TYPE).asInt());
                    }
                  } catch (IllegalArgumentException ex) {
                    LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
                        f.get(INTERNAL_COLUMN_NAME),
                        f.get(INTERNAL_SCHEMA_NAME),
                        f.get(INTERNAL_TABLE_NAME),
                        f.get(INTERNAL_COLUMN_TYPE)));
                    jdbcType = JDBCType.VARCHAR;
                  }
                  return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), jdbcType) {};
                })
                .collect(Collectors.toList()))
            .build())
        .collect(Collectors.toList());
  }


  public static void main(String[] args) throws Exception {
    final Source source = new DruidSource();
    LOGGER.info("starting source: {}", DruidSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", DruidSource.class);
  }

}
