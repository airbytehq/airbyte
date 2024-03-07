/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifierList;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.queryTable;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.SqlDatabase;
import io.airbyte.cdk.db.bigquery.BigQueryDatabase;
import io.airbyte.cdk.db.bigquery.BigQuerySourceOperations;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.relationaldb.AbstractDbSource;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQuerySource extends AbstractDbSource<StandardSQLTypeName, BigQueryDatabase> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySource.class);
  private static final String QUOTE = "`";

  public static final String CONFIG_DATASET_ID = "dataset_id";
  public static final String CONFIG_PROJECT_ID = "project_id";
  public static final String CONFIG_CREDS = "credentials_json";

  private JsonNode dbConfig;
  private final BigQuerySourceOperations sourceOperations = new BigQuerySourceOperations();

  protected BigQuerySource() {
    super(null);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final var conf = ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, config.get(CONFIG_PROJECT_ID).asText())
        .put(CONFIG_CREDS, config.get(CONFIG_CREDS).asText());
    if (config.hasNonNull(CONFIG_DATASET_ID)) {
      conf.put(CONFIG_DATASET_ID, config.get(CONFIG_DATASET_ID).asText());
    }
    return Jsons.jsonNode(conf.build());
  }

  @Override
  protected BigQueryDatabase createDatabase(final JsonNode sourceConfig) {
    dbConfig = Jsons.clone(sourceConfig);
    final BigQueryDatabase database = new BigQueryDatabase(sourceConfig.get(CONFIG_PROJECT_ID).asText(), sourceConfig.get(CONFIG_CREDS).asText());
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(toDatabaseConfig(sourceConfig));
    return database;
  }

  @Override
  public List<CheckedConsumer<BigQueryDatabase, Exception>> getCheckOperations(final JsonNode config) {
    final List<CheckedConsumer<BigQueryDatabase, Exception>> checkList = new ArrayList<>();
    checkList.add(database -> {
      if (database.query("select 1").count() < 1)
        throw new Exception("Unable to execute any query on the source!");
      else
        LOGGER.info("The source passed the basic query test!");
    });

    checkList.add(database -> {
      if (isDatasetConfigured(database)) {
        database.query(String.format("select 1 from %s where 1=0",
            getFullyQualifiedTableNameWithQuoting(getConfigDatasetId(database), "INFORMATION_SCHEMA.TABLES", getQuoteString())));
        LOGGER.info("The source passed the Dataset query test!");
      } else {
        LOGGER.info("The Dataset query test is skipped due to not configured datasetId!");
      }
    });

    return checkList;
  }

  @Override
  protected JsonSchemaType getAirbyteType(final StandardSQLTypeName columnType) {
    return sourceOperations.getAirbyteType(columnType);
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Collections.emptySet();
  }

  @Override
  protected List<TableInfo<CommonField<StandardSQLTypeName>>> discoverInternal(final BigQueryDatabase database) throws Exception {
    return discoverInternal(database, null);
  }

  @Override
  protected List<TableInfo<CommonField<StandardSQLTypeName>>> discoverInternal(final BigQueryDatabase database, final String schema) {
    final String projectId = dbConfig.get(CONFIG_PROJECT_ID).asText();
    final List<Table> tables =
        (isDatasetConfigured(database) ? database.getDatasetTables(getConfigDatasetId(database)) : database.getProjectTables(projectId));
    final List<TableInfo<CommonField<StandardSQLTypeName>>> result = new ArrayList<>();
    tables.stream().map(table -> TableInfo.<CommonField<StandardSQLTypeName>>builder()
        .nameSpace(table.getTableId().getDataset())
        .name(table.getTableId().getTable())
        .fields(Objects.requireNonNull(table.getDefinition().getSchema()).getFields().stream()
            .map(f -> {
              final StandardSQLTypeName standardType;
              if (f.getType().getStandardType() == StandardSQLTypeName.STRUCT && f.getMode() == Field.Mode.REPEATED) {
                standardType = StandardSQLTypeName.ARRAY;
              } else
                standardType = f.getType().getStandardType();

              return new CommonField<>(f.getName(), standardType);
            })
            .collect(Collectors.toList()))
        .build())
        .forEach(result::add);
    return result;
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final BigQueryDatabase database,
                                                          final List<TableInfo<CommonField<StandardSQLTypeName>>> tableInfos) {
    return Collections.emptyMap();
  }

  @Override
  protected String getQuoteString() {
    return QUOTE;
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(final BigQueryDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final CursorInfo cursorInfo,
                                                               final StandardSQLTypeName cursorFieldType) {
    return queryTableWithParams(database, String.format("SELECT %s FROM %s WHERE %s > ?",
        RelationalDbQueryUtils.enquoteIdentifierList(columnNames, getQuoteString()),
        getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString()),
        cursorInfo.getCursorField()),
        schemaName,
        tableName,
        sourceOperations.getQueryParameter(cursorFieldType, cursorInfo.getCursor()));
  }

  @Override
  protected AutoCloseableIterator<JsonNode> queryTableFullRefresh(final BigQueryDatabase database,
                                                                  final List<String> columnNames,
                                                                  final String schemaName,
                                                                  final String tableName,
                                                                  final SyncMode syncMode,
                                                                  final Optional<String> cursorField) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return queryTable(database, String.format("SELECT %s FROM %s",
        enquoteIdentifierList(columnNames, getQuoteString()),
        getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString())),
        tableName, schemaName);
  }

  @Override
  public boolean isCursorType(final StandardSQLTypeName standardSQLTypeName) {
    return true;
  }

  private AutoCloseableIterator<JsonNode> queryTableWithParams(final BigQueryDatabase database,
                                                               final String sqlQuery,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final QueryParameterValue... params) {
    final AirbyteStreamNameNamespacePair airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(sqlQuery, params);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private boolean isDatasetConfigured(final SqlDatabase database) {
    final JsonNode config = database.getSourceConfig();
    return config.hasNonNull(CONFIG_DATASET_ID) ? !config.get(CONFIG_DATASET_ID).asText().isEmpty() : false;
  }

  private String getConfigDatasetId(final SqlDatabase database) {
    return (isDatasetConfigured(database) ? database.getSourceConfig().get(CONFIG_DATASET_ID).asText() : "");
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new BigQuerySource();
    LOGGER.info("starting source: {}", BigQuerySource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", BigQuerySource.class);
  }

  @Override
  public void close() throws Exception {}

}
