/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.materialization;

import static java.util.Collections.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.gax.paging.Page;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.cloud.bigquery.TimePartitioning.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.apache.logging.log4j.core.lookup.StrSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// name is debatable :P but "BigQueryTypingAndDedupingOperations" is a really sad name
// `Schema` here is a com.google.cloud.bigquery.Schema
public class BigQueryMaterializationOperations implements MaterializationOperations<Schema> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryMaterializationOperations.class);

  private final BigQuery bigquery;

  public BigQueryMaterializationOperations(final BigQuery bigquery) {
    this.bigquery = bigquery;
  }

  /*
   * commentary: this is equivalent to existing normalization code. It's the whole "convert jsonschema types to sql types" thing.
   */
  @Override
  public Schema getTableSchema(ConfiguredAirbyteStream stream) {
    final JsonNode jsonSchema = stream.getStream().getJsonSchema();
    if (!jsonSchema.hasNonNull("properties")) {
      // TODO we probably should handle this in some reasonable way
      throw new IllegalArgumentException("Top-level stream schema must be an object; got " + jsonSchema);
    }
    List<Field> bqFields = new ArrayList<>();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");
    for (Iterator<Entry<String, JsonNode>> it = properties.fields(); it.hasNext(); ) {
      final Entry<String, JsonNode> field = it.next();
      String fieldName = field.getKey();
      JsonNode fieldSchema = field.getValue();

      // This is completely wrong, but the full implementation is really complicated
      String jsonTypeString = null;
      if (fieldSchema.hasNonNull("type")) {
        final JsonNode jsonType = fieldSchema.get("type");
        if (jsonType.isArray()) {
          // we have a schema like {type: [foo, bar]}
          // TODO handle multi-typed fields
          // for now, just pick the first non-null type
          for (JsonNode subtype : jsonType) {
            if (!"null".equals(subtype.asText())) {
              jsonTypeString = subtype.asText();
              break;
            }
          }
        } else {
          // presumably this is something like {type: foo}
          jsonTypeString = jsonType.asText();
        }
      }

      StandardSQLTypeName bqType;
      if (jsonTypeString != null) {
        bqType = switch (jsonTypeString) {
          // TODO handle airbyte_type nonsense
          case "string", "array", "object" -> StandardSQLTypeName.STRING;
          case "integer", "number" -> StandardSQLTypeName.NUMERIC;
          default -> StandardSQLTypeName.STRING;
        };
      } else {
        bqType = StandardSQLTypeName.STRING;
      }

      bqFields.add(Field.of(fieldName, bqType));
    }

    bqFields.add(Field.of("_airbyte_emitted_at", StandardSQLTypeName.TIMESTAMP));
    return Schema.of(bqFields);
  }

  /*
   * commentary: This is new code. dbt handled this for us transparently.
   */
  @Override
  public void createOrAlterTable(String datasetId, String tableName, Schema schema) {
    // TODO we probably should only do the getDataset().list() once per dataset
    // TODO maybe we put the raw table in a different dataset from the final table
    final Page<Table> page = bigquery.getDataset(datasetId).list();
    Table existingTable = null;
    for (Table table : page.getValues()) {
      if (tableName.equals(table.getTableId().getTable())) {
        existingTable = table;
        break;
      }
    }

    if (existingTable == null) {
      bigquery.create(TableInfo.newBuilder(
          TableId.of(datasetId, tableName),
          StandardTableDefinition.newBuilder()
              .setSchema(schema)
              .setClustering(Clustering.newBuilder().setFields(singletonList("_airbyte_emitted_at")).build())
              .setTimePartitioning(TimePartitioning.newBuilder(Type.DAY).setField("_airbyte_emitted_at").build())
              .build()
      ).build());
    } else {
      // TODO table exists - check existing table schema + alter table to match schema (maybe also alter partitoining/clustering)
      if (!schema.equals(existingTable.getDefinition().getSchema())) {
        LOGGER.warn("schema evolution is not yet implemented. Found schema " + existingTable.getDefinition().getSchema() + "; wanted schema " + schema);
      }
    }
  }

  /*
   * commentary: Some of this is equivalent to normalization code - the stuff around extracting JSON fields
   * and casting their types, etc.
   *
   * The stuff around explicitly writing a merge / insert is new; dbt handles that for us. That's also destination-specific;
   * e.g. some destinations might need explicit UPDATE and INSERT statements.
   *
   * The DELETE thing is new, and an improvement over normalization (where we need a separate DELETE call)
   */
  @Override
  public void mergeFromRawTable(String dataset, String rawTable, String finalTable, ConfiguredAirbyteStream stream, Schema schema) throws InterruptedException {
    // TODO handle non dedup sync modes (i.e. no PK) - probably needs to be an INSERT instead of MERGE
    // TODO handle CDC (multiple new raw records for a single PK)
    // TODO we should save this generated SQL. Just log it for now, but thats going to be super unergonomic
    // TODO we need to stick another _airbyte_eimtted_at > whatever clause somewhere maybe, to avoid a full table scan?
    /*
    WITH new_raw_records AS (
      SELECT * FROM dataset.rawTable
      WHERE _airbyte_emitted_at > (SELECT MAX(_airbyte_emitted_at) FROM dataset.finalTable)
    ), flattened_raw_records AS (
      SELECT
        json_extract(_airbyte_data, field1) AS field1,
        ...additional extract calls for each top-level field...
        _airbyte_emitted_at, other metadata columns...
      FROM new_raw_records
    ), typed_raw_records AS (
      CAST(field1 AS type1) AS field1,
      ...
      FROM flattened_raw_records
    )
    MERGE dataset.finalTable T
    USING dataset.typed_raw_records S
    ON T.primary_key = S.primary_key
    -- only generate this clause if stream contains the column + is incremenaldedup
    WHEN MATCHED AND _airbyte_cdc_deleted_at IS NOT NULL THEN
      DELETE
    WHEN MATCHED THEN
      UPDATE SET field1 = S.field1, ...
    WHEN NOT MATCHED THEN
      INSERT (field1, ..., _airbyte_emitted_at) VALUES (S.field1, ..., S._airbyte_emitted_at)
     */

    // TODO is there a better thing than coalesce(`0001-01-01 00:00:00')? i.e. check for table being empty -> remove the where clause
    String format = """
        MERGE ${dataset}.${final_table} T
        USING (
          WITH new_raw_records AS (
            SELECT * FROM ${dataset}.${raw_table}
            WHERE _airbyte_emitted_at > (SELECT COALESCE(MAX(_airbyte_emitted_at), '0001-01-01 00:00:00') FROM ${dataset}.${final_table})
          ), flattened_raw_records AS (
            SELECT
              ${extract_calls}
              _airbyte_emitted_at
            FROM new_raw_records
          )
          SELECT
            ${cast_calls}
            _airbyte_emitted_at
          FROM flattened_raw_records
        ) S
        ON T.${primary_key} = S.${primary_key}
        ${cdc_delete_clause}
        WHEN MATCHED THEN
          UPDATE SET ${set_calls}, _airbyte_emitted_at = S._airbyte_emitted_at
        WHEN NOT MATCHED THEN
          INSERT (${insert_fields}, _airbyte_emitted_at) VALUES (${insert_values}, S._airbyte_emitted_at)
        """;

    String extractCalls = schema.getFields()
        .stream()
        .filter(field -> !"_airbyte_emitted_at".equals(field.getName()))
        .map(field -> String.format("JSON_EXTRACT(_airbyte_data, '$.%1$s') AS %1$s,\n", field.getName()))
        .collect(Collectors.joining());

    String castCalls = schema.getFields()
        .stream()
        .filter(field -> !"_airbyte_emitted_at".equals(field.getName()))
        .map(field -> String.format("CAST(%1$s AS %2$s) AS %1$s,\n", field.getName(), field.getType()))
        .collect(Collectors.joining());

    // TODO check for CDC columns + sync mode; generate if necessary
    String cdcDeleteClause = "";

    String setCalls = schema.getFields()
        .stream()
        .filter(field -> !"_airbyte_emitted_at".equals(field.getName()))
        .map(field -> String.format("%1$s = S.%1$s", field.getName()))
        .collect(Collectors.joining(","));

    String insertFields = schema.getFields()
        .stream()
        .filter(field -> !"_airbyte_emitted_at".equals(field.getName()))
        .map(field -> String.format("%s", field.getName()))
        .collect(Collectors.joining(","));

    String insertValues = schema.getFields()
        .stream()
        .filter(field -> !"_airbyte_emitted_at".equals(field.getName()))
        .map(field -> String.format("S.%s", field.getName()))
        .collect(Collectors.joining(","));

    String mergeQuery = StrSubstitutor.replace(
        format,
        Map.of(
            "dataset", dataset,
            "raw_table", rawTable,
            "final_table", finalTable,
            "extract_calls", extractCalls,
            "cast_calls", castCalls,
            // TODO handle nested PK (maybe) + composite PK (maybe)
            "primary_key", stream.getPrimaryKey().get(0).get(0),
            "cdc_delete_clause", cdcDeleteClause,
            "set_calls", setCalls,
            "insert_fields", insertFields,
            "insert_values", insertValues
        )
    );

    LOGGER.info("Generated sql: {}", mergeQuery);

    bigquery.query(QueryJobConfiguration.newBuilder(mergeQuery).build());
  }
}
