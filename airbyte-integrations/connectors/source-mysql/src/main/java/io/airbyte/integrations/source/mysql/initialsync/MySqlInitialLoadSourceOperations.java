package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.MySqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mysql.MySqlSourceOperations;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;

public class MySqlInitialLoadSourceOperations extends MySqlSourceOperations {

  private final String transactionTimestamp;
  private final boolean shouldAugmentWithCdc;

  public MySqlInitialLoadSourceOperations(final String transactionTimestamp, final boolean shouldAugmentWithCdc) {
    super();
    this.transactionTimestamp = transactionTimestamp;
    this.shouldAugmentWithCdc = shouldAugmentWithCdc;
  }

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    if (shouldAugmentWithCdc) {
      // the first call communicates with the database. after that the result is cached.
      final ResultSetMetaData metadata = queryContext.getMetaData();
      final int columnCount = metadata.getColumnCount();
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      for (int i = 1; i <= columnCount; i++) {
        // convert to java types that will convert into reasonable json.
        copyToJsonField(queryContext, i, jsonNode);
      }

      final MySqlCdcConnectorMetadataInjector metadataInjector = new MySqlCdcConnectorMetadataInjector();
      metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(jsonNode, transactionTimestamp);
      return jsonNode;
    } else {
      return super.rowToJson(queryContext);
    }
  }
}
