/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.microsoft.sqlserver.jdbc.SQLServerException;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying mssql
 */
public class MssqlQueryUtils {
  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlQueryUtils.class);
  public static final String INDEX_QUERY = "EXEC sp_helpindex N'%s'";
  public record Index(
      @JsonProperty("index_name") String name,
      @JsonProperty("index_description") String description,
      @JsonProperty("index_keys") String keys
  ) { }

  public static void getIndexInfoForStreams(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog, final String quoteString) {
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = stream.getStream().getNamespace();
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      LOGGER.info("Discovering indexes for table {}", fullTableName);
      try {
        final String query = INDEX_QUERY.formatted(fullTableName);
        LOGGER.debug("Index lookup query: {}", query);
        final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(query).executeQuery(),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        if (jsonNodes != null) {
          jsonNodes.stream().map(node -> Jsons.convertValue(node, Index.class))
              .forEach(i -> LOGGER.info(String.valueOf(i)));
        }
      } catch (final Exception ex) {
        LOGGER.info("Failed to get index for {}", fullTableName);
      }
    }

  }
}
