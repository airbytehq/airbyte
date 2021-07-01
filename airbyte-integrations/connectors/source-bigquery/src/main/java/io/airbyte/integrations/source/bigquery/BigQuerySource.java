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

package io.airbyte.integrations.source.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.Databases;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.db.bigquery.BigQueryUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.SourceJdbcUtils;
import io.airbyte.integrations.source.relationaldb.AbstractRelationalDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

public class BigQuerySource extends AbstractRelationalDbSource<StandardSQLTypeName, BigQueryDatabase> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySource.class);

  // TODO insert your driver name. Ex: "com.microsoft.sqlserver.jdbc.SQLServerDriver"
  static final String DRIVER_CLASS = "driver_name_here";
  static final String CONFIG_DATASET_ID = "dataset_id";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_DATASET_LOCATION = "dataset_location";
  static final String CONFIG_CREDS = "credentials_json";
  private String quote = "";
  private JsonNode dbConfig;

  public BigQuerySource() {
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    return Jsons.jsonNode(ImmutableMap.builder()
            .put(CONFIG_PROJECT_ID, config.get(CONFIG_PROJECT_ID).asText())
            .put(CONFIG_CREDS, config.get(CONFIG_CREDS).asText())
            .put(CONFIG_DATASET_ID, config.get(CONFIG_DATASET_ID).asText())
            .build());
  }

  @Override
  protected BigQueryDatabase createDatabase(JsonNode config) throws Exception {
    dbConfig = Jsons.clone(config);
    return Databases.createBigQueryDatabase(config.get(CONFIG_PROJECT_ID).asText(), config.get(CONFIG_CREDS).asText(), config.get(CONFIG_DATASET_ID).asText());
  }

  @Override
  public List<CheckedConsumer<BigQueryDatabase, Exception>> getCheckOperations(JsonNode config) throws Exception {
    return new ArrayList<>();
  }

  @Override
  protected JsonSchemaPrimitive getType(StandardSQLTypeName columnType) {
    return BigQueryUtils.getType(columnType);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.emptySet();
  }

  @Override
  protected List<TableInfo<CommonField<StandardSQLTypeName>>> discoverInternal(BigQueryDatabase database) throws Exception {
    List<Table> nameSpaceTables = database.getNameSpaceTables(dbConfig.get(CONFIG_PROJECT_ID).asText());

    return null;
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(BigQueryDatabase database, List<TableInfo<CommonField<StandardSQLTypeName>>> tableInfos) {
    return null;
  }

  @Override
  protected String getQuoteString() {
    return quote;
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(BigQueryDatabase database, List<String> columnNames, String schemaName, String tableName, String cursorField, StandardSQLTypeName cursorFieldType, String cursor) {
    return null;
  }

  public static void main(String[] args) throws Exception {
    final Source source = new BigQuerySource();
    LOGGER.info("starting source: {}", BigQuerySource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", BigQuerySource.class);
  }
}
