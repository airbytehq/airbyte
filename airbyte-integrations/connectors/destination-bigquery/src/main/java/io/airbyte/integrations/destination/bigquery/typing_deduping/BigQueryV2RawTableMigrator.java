package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.V2RawTableMigrator;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryV2RawTableMigrator implements V2RawTableMigrator<TableDefinition> {
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryV2RawTableMigrator.class);

  private final BigQuery bq;

  public BigQueryV2RawTableMigrator(final BigQuery bq) {
    this.bq = bq;
  }


  @Override
  public void migrateIfNecessary(final StreamConfig streamConfig) throws InterruptedException {
    final Table rawTable = bq.getTable(TableId.of(streamConfig.id().rawNamespace(), streamConfig.id().rawName()));
    if (rawTable != null && rawTable.exists()) {
      final Schema existingRawSchema = rawTable.getDefinition().getSchema();
      final FieldList fields = existingRawSchema.getFields();
      if (fields.stream().noneMatch(f -> JavaBaseConstants.COLUMN_NAME_DATA.equals(f.getName()))) {
        throw new IllegalStateException("Table does not have a column named _airbyte_data. We are likely colliding with a completely different table.");
      }
      final Field dataColumn = fields.get(JavaBaseConstants.COLUMN_NAME_DATA);
      if (dataColumn.getType() == LegacySQLTypeName.JSON) {
        LOGGER.info("Raw table has _airbyte_data of type JSON. Migrating to STRING.");
        bq.query(QueryJobConfiguration.of(
            new StringSubstitutor(Map.of(
                "raw_table", streamConfig.id().rawTableId(BigQuerySqlGenerator.QUOTE)
            )).replace(
                """
                    CREATE OR REPLACE TABLE ${raw_table}
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
                    """
            )
        ));
      }
    }
  }
}
