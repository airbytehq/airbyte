package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;
import io.airbyte.integrations.source.mysql.MySqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mysql.MySqlSourceOperations;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;
import java.util.Optional;

public class MySqlInitialLoadSourceOperations extends MySqlSourceOperations {

  private final Optional<CdcMetadataInjector> metadataInjector;

  public MySqlInitialLoadSourceOperations(final Optional<CdcMetadataInjector> metadataInjector) {
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
    private final MysqlDebeziumStateAttributes stateAttributes;
    private final MySqlCdcConnectorMetadataInjector metadataInjector;

    public CdcMetadataInjector(final String transactionTimestamp, final MysqlDebeziumStateAttributes stateAttributes,
        final MySqlCdcConnectorMetadataInjector metadataInjector) {
      this.transactionTimestamp = transactionTimestamp;
      this.stateAttributes = stateAttributes;
      this.metadataInjector = metadataInjector;
    }

    private void inject(final ObjectNode record) {
      metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, stateAttributes);
    }
  }
}
