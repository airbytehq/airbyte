/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableId;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.V2TableMigrator;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryV2TableMigrator implements V2TableMigrator {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryV2TableMigrator.class);

  private final BigQuery bq;

  public BigQueryV2TableMigrator(final BigQuery bq) {
    this.bq = bq;
  }

  @Override
  public void migrateIfNecessary(final StreamConfig streamConfig) throws InterruptedException {
    final Table rawTable = bq.getTable(TableId.of(streamConfig.getId().getRawNamespace(), streamConfig.getId().getRawName()));
    if (rawTable != null && rawTable.exists()) {
      final Schema existingRawSchema = rawTable.getDefinition().getSchema();
      final FieldList fields = existingRawSchema.getFields();
      if (fields.stream().noneMatch(f -> JavaBaseConstants.COLUMN_NAME_DATA.equals(f.getName()))) {
        throw new IllegalStateException(
            "Table does not have a column named _airbyte_data. We are likely colliding with a completely different table.");
      }
      final Field dataColumn = fields.get(JavaBaseConstants.COLUMN_NAME_DATA);
      if (dataColumn.getType() == LegacySQLTypeName.JSON) {
        LOGGER.info("Raw table has _airbyte_data of type JSON. Migrating to STRING.");
        final String tmpRawTableId = BigQuerySqlGenerator.QUOTE + streamConfig.getId().getRawNamespace() + BigQuerySqlGenerator.QUOTE + "."
            + BigQuerySqlGenerator.QUOTE + streamConfig.getId().getRawName() + "_airbyte_tmp" + BigQuerySqlGenerator.QUOTE;
        bq.query(QueryJobConfiguration.of(
            new StringSubstitutor(Map.of(
                "raw_table", streamConfig.getId().rawTableId(BigQuerySqlGenerator.QUOTE),
                "tmp_raw_table", tmpRawTableId,
                "real_raw_table", BigQuerySqlGenerator.QUOTE + streamConfig.getId().getRawName() + BigQuerySqlGenerator.QUOTE)).replace(
                    // In full refresh / append mode, standard inserts is creating a non-partitioned raw table.
                    // (possibly also in overwrite mode?).
                    // We can't just CREATE OR REPLACE the table because bigquery will complain that we're trying to
                    // change the partitioning scheme.
                    // Do an explicit CREATE tmp + DROP + RENAME, similar to how we overwrite the final tables in
                    // OVERWRITE mode.
                    """
                    CREATE TABLE ${tmp_raw_table}
                    PARTITION BY DATE(_airbyte_extracted_at)
                    CLUSTER BY _airbyte_extracted_at
                    AS (
                      SELECT
                        _airbyte_raw_id,
                        _airbyte_extracted_at,
                        _airbyte_loaded_at,
                        to_json_string(_airbyte_data) as _airbyte_data
                      FROM ${raw_table}
                    );
                    DROP TABLE IF EXISTS ${raw_table};
                    ALTER TABLE ${tmp_raw_table} RENAME TO ${real_raw_table};
                    """)));
        LOGGER.info("Completed Data column Migration for stream {}", streamConfig.getId().getRawName());
      } else {
        LOGGER.info("No Data column Migration Required for stream {}", streamConfig.getId().getRawName());
      }
    }
  }

}
