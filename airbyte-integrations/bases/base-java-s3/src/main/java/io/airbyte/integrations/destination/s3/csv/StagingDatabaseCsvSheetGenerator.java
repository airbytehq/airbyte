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
 * <p>
 * In 1s1t mode, the column ordering is also different (raw_id, extracted_at, loaded_at, data). Note
 * that the loaded_at column is rendered as an empty string; callers are expected to configure their
 * destination to parse this as NULL. For example, Snowflake's COPY into command accepts a NULL_IF
 * parameter, and Redshift accepts an EMPTYASNULL option.
 */
public class StagingDatabaseCsvSheetGenerator implements CsvSheetGenerator {

  private final boolean use1s1t;
  private final List<String> header;

  public StagingDatabaseCsvSheetGenerator() {
    use1s1t = TypingAndDedupingFlag.isDestinationV2();
    this.header = use1s1t ? JavaBaseConstants.V2_COLUMN_NAMES : JavaBaseConstants.LEGACY_COLUMN_NAMES;
  }

  // TODO is this even used anywhere?
  @Override
  public List<String> getHeaderRow() {
    return header;
  }

  @Override
  public List<Object> getDataRow(final UUID id, final AirbyteRecordMessage recordMessage) {
    return getDataRow(id, Jsons.serialize(recordMessage.getData()), recordMessage.getEmittedAt());
  }

  @Override
  public List<Object> getDataRow(final JsonNode formattedData) {
    return new LinkedList<>(Collections.singletonList(Jsons.serialize(formattedData)));
  }

  @Override
  public List<Object> getDataRow(final UUID id, final String formattedString, final long emittedAt) {
    if (use1s1t) {
      return List.of(
          id,
          Timestamp.from(Instant.ofEpochMilli(emittedAt)),
          "",
          formattedString);
    } else {
      return List.of(
          id,
          formattedString,
          Timestamp.from(Instant.ofEpochMilli(emittedAt)));
    }
  }

}
