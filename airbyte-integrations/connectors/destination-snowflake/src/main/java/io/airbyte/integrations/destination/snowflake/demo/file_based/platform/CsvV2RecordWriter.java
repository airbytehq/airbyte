package io.airbyte.integrations.destination.snowflake.demo.file_based.platform;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.UUID;

/**
 * Other implementations exist, e.g. avro, parquet, jsonl. Platform would provide generic implementations,
 * though destinations could provide their own implementations if they want to do something fancy.
 * <p>
 * This implementation would write the DV2 CSV format (raw_id, extracted_at, data, loaded_at; loaded_at is always null).
 */
public class CsvV2RecordWriter implements RecordWriter {
  private final String path;
  private String filename;
  @Override
  public String getCurrentFilename() {
    return path + "/" + filename + ".csv";
  }

  @Override
  public void write(final AirbyteRecordMessage record) {
    // do something like StagingDatabaseCsvSheetGenerator
  }

  @Override
  public void rotateFile() {
    // flush to the current file

    filename = UUID.randomUUID().toString();
  }
}
