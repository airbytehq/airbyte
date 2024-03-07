/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresSourceOperations;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;
import java.util.Objects;
import java.util.Optional;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_LSN;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;

public class CtidPostgresSourceOperations extends PostgresSourceOperations {

  private final Optional<CdcMetadataInjector> cdcMetadataInjector;

  public CtidPostgresSourceOperations(final Optional<CdcMetadataInjector> cdcMetadataInjector) {
    super();
    this.cdcMetadataInjector = cdcMetadataInjector;
  }

  private static final String CTID = "ctid";

  public RowDataWithCtid recordWithCtid(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final ResultSetMetaData metadata = queryContext.getMetaData();
    final int columnCount = metadata.getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    String ctid = null;
    for (int i = 1; i <= columnCount; i++) {
      final String columnName = metadata.getColumnName(i);
      if (columnName.equalsIgnoreCase(CTID)) {
        ctid = queryContext.getString(i);
        continue;
      }

      // convert to java types that will convert into reasonable json.
      copyToJsonField(queryContext, i, jsonNode);
    }

    if (Objects.nonNull(cdcMetadataInjector) && cdcMetadataInjector.isPresent()) {
      cdcMetadataInjector.get().inject(jsonNode);
    }

    assert Objects.nonNull(ctid);
    return new RowDataWithCtid(jsonNode, ctid);
  }

  public record RowDataWithCtid(JsonNode data, String ctid) {

  }

  public static class CdcMetadataInjector {

    private final String transactionTimestamp;
    private final long lsn;

    public CdcMetadataInjector(final String transactionTimestamp,
                               final long lsn) {
      this.transactionTimestamp = transactionTimestamp;
      this.lsn = lsn;
    }

    private void inject(final ObjectNode record) {
      record.put(CDC_UPDATED_AT, transactionTimestamp);
      record.put(CDC_LSN, lsn);
      record.put(CDC_DELETED_AT, (String) null);
    }

  }

}
