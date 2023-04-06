/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.materialization;

import com.google.api.gax.paging.Page;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.Table;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

public class BigQueryMaterializationOperations {

  private final BigQuery bigquery;

  public BigQueryMaterializationOperations(final BigQuery bigquery) {
    this.bigquery = bigquery;
  }

  /*
   * commentary: this is equivalent to existing normalization code.
   */
  public Schema getTableSchema(ConfiguredAirbyteStream stream) {
    // TODO
    return null;
  }

  /*
   * commentary: This is new code. dbt handled this for us transparently.
   */
  public void createOrAlterTable(String datasetId, String tableName, Schema schema) {
    // TODO we probably should only do the getDataset().list() once per dataset
    // TODO maybe we put the raw table in a different dataset from the final table
    final Page<Table> page = bigquery.getDataset(datasetId).list();
    for (Table table : page.getValues()) {
      if (tableName.equals(table.getFriendlyName())) {
        // TODO table exists - check existing table schema + alter table to match schema (maybe also alter partitoining/clustering)
      } else {
        // TODO table doesn't exist - create it with schema + partitoining + clustering
      }
    }
  }

  /*
   * commentary: Some of this is equivalent to normalization code - the stuff around extracting JSON fields
   * and casting their types, etc.
   *
   * The stuff around explicitly writing a merge / insert is new; dbt handles that for us.
   */
  public void mergeFromRawTable(String dataset, String rawTable, String finalTable, Schema schema) {
    // TODO generate a SQL query >.>
    // TODO handle non dedup sync modes (i.e. no PK) - probably needs to be an INSERT instead of MERGE
    // TODO handle CDC (i.e. multiple new raw records for a single PK)
    /*
    WITH new_raw_records AS (
      SELECT * FROM dataset.rawTable
      WHERE _airbyte_emitted_at > (SELECT MAX(_airbyte_emitted_at) FROM dataset.finalTable)
    ), flattened_raw_records AS (
      SELECT
        json_extract(_airbyte_data, field1) AS field1,
        ...additional extract calls for each top-level field...
      FROM new_raw_records
    ), typed_raw_records AS (
      CAST(field1 AS type1) AS field1,
      ...
      FROM flattened_raw_records
    )
    MERGE dataset.finalTable T
    USING dataset.typed_raw_records S
    ON T.primary_key = S.primary_key
    WHEN MATCHED THEN
      UPDATE SET field1 = S.field1, ...
    WHEN NOT MATCHED THEN
      INSERT (field1, ...) VALUES (S.field1, ...)
     */
  }
}
