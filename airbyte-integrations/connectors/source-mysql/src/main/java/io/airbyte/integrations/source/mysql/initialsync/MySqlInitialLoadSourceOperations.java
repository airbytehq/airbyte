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

  private final String transactionTimestamp;
  private final Optional<MysqlDebeziumStateAttributes> debeziumStateAttributes;

  public MySqlInitialLoadSourceOperations(final String transactionTimestamp, final Optional<MysqlDebeziumStateAttributes> debeziumStateAttributes) {
    super();
    this.transactionTimestamp = transactionTimestamp;
    this.debeziumStateAttributes = debeziumStateAttributes;
  }

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    if (debeziumStateAttributes.isPresent()) {
      // the first call communicates with the database. after that the result is cached.
      final ResultSetMetaData metadata = queryContext.getMetaData();
      final int columnCount = metadata.getColumnCount();
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      for (int i = 1; i <= columnCount; i++) {
        // convert to java types that will convert into reasonable json.
        copyToJsonField(queryContext, i, jsonNode);
      }

      final MySqlCdcConnectorMetadataInjector metadataInjector = new MySqlCdcConnectorMetadataInjector();
      metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(jsonNode, transactionTimestamp, debeziumStateAttributes.get());
      return jsonNode;
    } else {
      return super.rowToJson(queryContext);
    }
  }
}
