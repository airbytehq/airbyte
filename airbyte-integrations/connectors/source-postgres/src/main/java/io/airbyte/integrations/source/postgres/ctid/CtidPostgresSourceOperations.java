/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.AirbyteRecordData;
import io.airbyte.integrations.source.postgres.PostgresSourceOperations;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcConnectorMetadataInjector;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;

public class CtidPostgresSourceOperations extends PostgresSourceOperations {

  private final Optional<PostgresCdcConnectorMetadataInjector> cdcMetadataInjector;

  public CtidPostgresSourceOperations(final Optional<PostgresCdcConnectorMetadataInjector> cdcMetadataInjector) {
    super();
    this.cdcMetadataInjector = cdcMetadataInjector;
  }

  private static final String CTID = "ctid";

  public RowDataWithCtid recordWithCtid(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final AirbyteRecordData airbyteRecordData = super.convertDatabaseRowToAirbyteRecordData(queryContext);
    final ObjectNode jsonNode = (ObjectNode) airbyteRecordData.rawRowData();
    // We need to modify this base record by (1) extracting the CTID field and (2) injecting the CDC
    // metadata
    if (Objects.nonNull(cdcMetadataInjector) && cdcMetadataInjector.isPresent()) {
      cdcMetadataInjector.get().addMetaDataToRowsFetchedOutsideDebezium(jsonNode);
    }
    String ctid = jsonNode.remove(CTID).asText();
    AirbyteRecordData recordData = new AirbyteRecordData(jsonNode, airbyteRecordData.meta());

    assert Objects.nonNull(ctid);
    return new RowDataWithCtid(recordData, ctid);
  }

  public record RowDataWithCtid(AirbyteRecordData recordData, String ctid) {}

}
