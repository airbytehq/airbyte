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

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSource.class);

  // todo (cgardens) - clean up passing the dialect as null versus explicitly adding the case to the
  // constructor.
  public MssqlSource() {
    super("com.microsoft.sqlserver.jdbc.SQLServerDriver", null);
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode mssqlConfig) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", mssqlConfig.get("username").asText())
        .put("password", mssqlConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:sqlserver://%s:%s;databaseName=%s",
            mssqlConfig.get("host").asText(),
            mssqlConfig.get("port").asText(),
            mssqlConfig.get("database").asText()))
        .build());
  }

  @Override
  protected String getCurrentDatabaseName(DSLContext ctx) {
    return ctx.fetch("SELECT db_name()").get(0).get(0, String.class);
  }

  @Override
  protected List<TableInfo> getTables(final Database database) throws Exception {
    return database.query(ctx -> {
      final Result<Record> fetch = ctx.fetch("SELECT * FROM INFORMATION_SCHEMA.TABLES;");
      final List<String> tableNames = fetch.stream().map(r -> r.get("TABLE_NAME", String.class)).collect(Collectors.toList());
      // https://stackoverflow.com/a/2418665/4195169
      return tableNames.stream().map(tableName -> {
        final Result<Record> fetch1 = ctx.fetch(String.format("\n" +
            "SELECT \n"
            + "    c.name 'column_name',\n"
            + "    t.Name 'data_type'\n"
            + "FROM    \n"
            + "    sys.columns c\n"
            + "INNER JOIN \n"
            + "    sys.types t ON c.user_type_id = t.user_type_id\n"
            + "LEFT OUTER JOIN \n"
            + "    sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id\n"
            + "LEFT OUTER JOIN \n"
            + "    sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id\n"
            + "WHERE\n"
            + "    c.object_id = OBJECT_ID('%s')", tableName));
        final List<Field> fields = fetch1
            .stream()
            .map(r -> {
              final String columnName = r.get("column_name", String.class);
              final String dataType = r.get("data_type", String.class);
              final JsonSchemaPrimitive jsonType = getType(dataType);
              return Field.of(columnName, jsonType);
            }).collect(Collectors.toList());

        return new TableInfo(tableName, fields);
      })
          .collect(Collectors.toList());
    });
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MssqlSource();
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

  private static JsonSchemaPrimitive getType(String mssqlType) {
    // mssql types:
    // https://docs.microsoft.com/en-us/sql/t-sql/data-types/data-types-transact-sql?view=sql-server-ver15
    return switch (mssqlType) {
      case "bigint", "numeric", "bit", "smallint", "decimal", "int", "tinyint", "float" -> JsonSchemaPrimitive.NUMBER;
      default -> JsonSchemaPrimitive.STRING;
    };
  }

}
