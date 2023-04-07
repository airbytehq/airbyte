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
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.cloud.bigquery.TimePartitioning.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
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
  public Schema getTableSchema(ConfiguredAirbyteStream stream) {
    final JsonNode jsonSchema = stream.getStream().getJsonSchema();
    if (jsonSchema.hasNonNull("properties")) {
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
        };
      } else {
        bqType = StandardSQLTypeName.STRING;
      }

      bqFields.add(Field.of(fieldName, bqType));
    }
    return Schema.of(bqFields);
  }

  /*
   * commentary: This is new code. dbt handled this for us transparently.
   */
  public void createOrAlterTable(String datasetId, String tableName, Schema schema) {
    // TODO we probably should only do the getDataset().list() once per dataset
    // TODO maybe we put the raw table in a different dataset from the final table
    final Page<Table> page = bigquery.getDataset(datasetId).list();
    boolean tableExists = false;
    for (Table table : page.getValues()) {
      if (tableName.equals(table.getFriendlyName())) {
        tableExists = true;
        break;
      }
    }
    
    if (!tableExists) {
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
      LOGGER.warn("schema evolution is not yet implemented");
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
  public void mergeFromRawTable(String dataset, String rawTable, String finalTable, ConfiguredAirbyteStream stream) {
    // TODO generate a SQL query >.>
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
      INSERT (field1, ...) VALUES (S.field1, ...)
     */
  }
}
