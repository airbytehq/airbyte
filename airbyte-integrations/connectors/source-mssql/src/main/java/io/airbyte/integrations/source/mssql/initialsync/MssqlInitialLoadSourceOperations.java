/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MssqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mssql.MssqlSourceOperations;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;
import java.util.Optional;

public class MssqlInitialLoadSourceOperations extends MssqlSourceOperations {

  private final Optional<CdcMetadataInjector> metadataInjector;

  public MssqlInitialLoadSourceOperations(final Optional<CdcMetadataInjector> metadataInjector) {
    super();
    this.metadataInjector = metadataInjector;
  }

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    if (metadataInjector.isPresent()) {
      // the first call communicates with the database. after that the result is cached.
      final ResultSetMetaData metadata = queryContext.getMetaData();
      final int columnCount = metadata.getColumnCount();
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      for (int i = 1; i <= columnCount; i++) {
        // attempt to access the column. this allows us to know if it is null before we do type-specific
        // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
        // checking for null values with jdbc.
        queryContext.getObject(i);
        if (queryContext.wasNull()) {
          continue;
        }

        // convert to java types that will convert into reasonable json.
        copyToJsonField(queryContext, i, jsonNode);
      }

      metadataInjector.get().inject(jsonNode);
      return jsonNode;
    } else {
      return super.rowToJson(queryContext);
    }
  }

  public static class CdcMetadataInjector {

    private final String transactionTimestamp;
    private final MssqlDebeziumStateAttributes stateAttributes;
    private final MssqlCdcConnectorMetadataInjector metadataInjector;

    public CdcMetadataInjector(final String transactionTimestamp,
                               final MssqlDebeziumStateAttributes stateAttributes,
                               final MssqlCdcConnectorMetadataInjector metadataInjector) {
      this.transactionTimestamp = transactionTimestamp;
      this.stateAttributes = stateAttributes;
      this.metadataInjector = metadataInjector;
    }

    private void inject(final ObjectNode record) {
      metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, stateAttributes);
    }

  }

}
