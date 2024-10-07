/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_EVENT_SERIAL_NO;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

public class MssqlCdcConnectorMetadataInjector implements CdcMetadataInjector<MssqlDebeziumStateAttributes> {

  private final long emittedAtConverted;

  // This now makes this class stateful. Please make sure to use the same instance within a sync
  private final AtomicLong recordCounter = new AtomicLong(1);
  private static final long ONE_HUNDRED_MILLION = 100_000_000;
  private static MssqlCdcConnectorMetadataInjector mssqlCdcConnectorMetadataInjector;

  private MssqlCdcConnectorMetadataInjector(final Instant emittedAt) {
    this.emittedAtConverted = emittedAt.getEpochSecond() * ONE_HUNDRED_MILLION;
  }

  public static MssqlCdcConnectorMetadataInjector getInstance(final Instant emittedAt) {
    if (mssqlCdcConnectorMetadataInjector == null) {
      mssqlCdcConnectorMetadataInjector = new MssqlCdcConnectorMetadataInjector(emittedAt);
    }

    return mssqlCdcConnectorMetadataInjector;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final String commitLsn = source.get("commit_lsn").asText();
    final String eventSerialNo = source.get("event_serial_no").asText();
    event.put(CDC_LSN, commitLsn);
    event.put(CDC_EVENT_SERIAL_NO, eventSerialNo);
    event.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record,
                                                      final String transactionTimestamp,
                                                      final MssqlDebeziumStateAttributes debeziumStateAttributes) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_EVENT_SERIAL_NO, 1);
    record.put(CDC_LSN, debeziumStateAttributes.lsn().toString());
    record.put(CDC_DELETED_AT, (String) null);
    record.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("schema").asText();
  }

  @Override
  public String name(JsonNode source) {
    return source.get("table").asText();
  }

  private Long getCdcDefaultCursor() {
    return this.emittedAtConverted + this.recordCounter.getAndIncrement();
  }

}
