/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.UUID;

/**
 * A CsvSheetGenerator that produces data in the format expected by JdbcSqlOperations. See
 * JdbcSqlOperations#createTableQuery.
 * <p>
 * This intentionally does not extend {@link BaseSheetGenerator}, because it needs the columns in a
 * different order (ABID, JSON, timestamp) vs (ABID, timestamp, JSON)
 */
public class StagingDatabaseCsvSheetGenerator implements CsvSheetGenerator {

  private static final List<String> LEGACY_COLUMN_NAMES = List.of(
      JavaBaseConstants.COLUMN_NAME_AB_ID,
      JavaBaseConstants.COLUMN_NAME_DATA,
      JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  // TODO does this need to have loaded_at explicitly?
  // TODO does this need to be in a different order? (raw_id, extracted_at, loaded_at, data)
  private static final List<String> V2_COLUMN_NAMES = List.of(
      JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
      JavaBaseConstants.COLUMN_NAME_DATA,
      JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);

  private final List<String> header;

  public StagingDatabaseCsvSheetGenerator() {
    if (TypingAndDedupingFlag.isDestinationV2()) {
      this.header = V2_COLUMN_NAMES;
    } else {
      this.header = LEGACY_COLUMN_NAMES;
    }
  }

  @Override
  public List<String> getHeaderRow() {
    return header;
  }

  @Override
  public List<Object> getDataRow(final UUID id, final AirbyteRecordMessage recordMessage) {
    return List.of(
        id,
        Jsons.serialize(recordMessage.getData()),
        Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
  }

  @Override
  public List<Object> getDataRow(final JsonNode formattedData) {
    return new LinkedList<>(Collections.singletonList(Jsons.serialize(formattedData)));
  }

  @Override
  public List<Object> getDataRow(final UUID id, final String formattedString, final long emittedAt) {
    return List.of(
        id,
        formattedString,
        Timestamp.from(Instant.ofEpochMilli(emittedAt)));
  }

}
