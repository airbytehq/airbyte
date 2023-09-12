package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer;

import io.airbyte.integrations.destination.snowflake.demo.file_based.platform.record_renderer.RecordRenderer;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

/**
 * Other implementations exist, e.g. avro, parquet, jsonl. Platform would provide generic implementations,
 * though destinations could provide their own implementations if they want to do something fancy.
 * <p>
 * This implementation would write the DV2 CSV format (raw_id, extracted_at, data, loaded_at; loaded_at is always null).
 */
public class CsvV2RecordRenderer implements RecordRenderer {

  @Override
  public byte[] render(final AirbyteRecordMessage record) {
    // Do the same thing as StagingDatabaseCsvSheetGenerator
    return null;
  }
}
