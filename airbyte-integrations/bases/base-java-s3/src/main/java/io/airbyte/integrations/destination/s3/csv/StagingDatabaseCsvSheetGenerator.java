/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
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

  /**
   * This method is implemented for clarity, but not actually used. S3StreamCopier disables headers on
   * S3CsvWriter.
   */
  @Override
  public List<String> getHeaderRow() {
    return List.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
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

}
