/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.cdk.db.DbAnalyticsUtils.dataTypesSerializationErrorMessage;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.AirbyteRecordData;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresSourceOperations;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcConnectorMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.LoggerFactory;

public class CtidPostgresSourceOperations extends PostgresSourceOperations {

  private static final org.slf4j.Logger LOGGER = LoggerFactory.getLogger(CtidPostgresSourceOperations.class);

  private final Optional<PostgresCdcConnectorMetadataInjector> cdcMetadataInjector;

  public CtidPostgresSourceOperations(final Optional<PostgresCdcConnectorMetadataInjector> cdcMetadataInjector) {
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
    final List<AirbyteRecordMessageMetaChange> metaChanges = new ArrayList<>();
    for (int i = 1; i <= columnCount; i++) {
      final String columnName = metadata.getColumnName(i);
      final String columnTypeName = metadata.getColumnTypeName(i);
      try {
        if (columnName.equalsIgnoreCase(CTID)) {
          ctid = queryContext.getString(i);
          continue;
        }

        // convert to java types that will convert into reasonable json.
        copyToJsonField(queryContext, i, jsonNode);
      } catch (Exception e) {
        LOGGER.info("Failed to serialize column: {}, of type {}, with error {}", columnName, columnTypeName, e.getMessage());
        AirbyteTraceMessageUtility.emitAnalyticsTrace(dataTypesSerializationErrorMessage());
        metaChanges.add(
            new AirbyteRecordMessageMetaChange()
                .withField(columnName)
                .withChange(Change.NULLED)
                .withReason(Reason.SOURCE_SERIALIZATION_ERROR));
      }
    }

    if (Objects.nonNull(cdcMetadataInjector) && cdcMetadataInjector.isPresent()) {
      cdcMetadataInjector.get().addMetaDataToRowsFetchedOutsideDebezium(jsonNode);
    }

    assert Objects.nonNull(ctid);
    return new RowDataWithCtid(new AirbyteRecordData(jsonNode, new AirbyteRecordMessageMeta().withChanges(metaChanges)), ctid);
  }

  public record RowDataWithCtid(AirbyteRecordData recordData, String ctid) {}

}
