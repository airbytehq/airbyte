/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.SqlDatabase;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.StringJoiner;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class for methods to query a relational db.
 */
public class RelationalDbQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(RelationalDbQueryUtils.class);

  public record TableSizeInfo(Long tableSize, Long avgRowLength) {}

  public static String getIdentifierWithQuoting(final String identifier, final String quoteString) {
    // double-quoted values within a database name or column name should be wrapped with extra
    // quoteString
    if (identifier.startsWith(quoteString) && identifier.endsWith(quoteString)) {
      return quoteString + quoteString + identifier + quoteString + quoteString;
    } else {
      return quoteString + identifier + quoteString;
    }
  }

  public static String enquoteIdentifierList(final List<String> identifiers, final String quoteString) {
    final StringJoiner joiner = new StringJoiner(",");
    for (final String identifier : identifiers) {
      joiner.add(getIdentifierWithQuoting(identifier, quoteString));
    }
    return joiner.toString();
  }

  /**
   * @return fully qualified table name with the schema (if a schema exists) in quotes.
   */
  public static String getFullyQualifiedTableNameWithQuoting(final String nameSpace, final String tableName, final String quoteString) {
    return (nameSpace == null || nameSpace.isEmpty() ? getIdentifierWithQuoting(tableName, quoteString)
        : getIdentifierWithQuoting(nameSpace, quoteString) + "." + getIdentifierWithQuoting(tableName, quoteString));
  }

  /**
   * @return fully qualified table name with the schema (if a schema exists) without quotes.
   */
  public static String getFullyQualifiedTableName(final String schemaName, final String tableName) {
    return schemaName != null ? schemaName + "." + tableName : tableName;
  }

  /**
   * @return the input identifier with quotes.
   */
  public static String enquoteIdentifier(final String identifier, final String quoteString) {
    return quoteString + identifier + quoteString;
  }

  public static <Database extends SqlDatabase> AutoCloseableIterator<JsonNode> queryTable(final Database database,
                                                                                          final String sqlQuery,
                                                                                          final String tableName,
                                                                                          final String schemaName) {
    final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        LOGGER.info("Queueing query: {}", sqlQuery);
        final Stream<JsonNode> stream = database.unsafeQuery(sqlQuery);
        return AutoCloseableIterators.fromStream(stream, airbyteStreamNameNamespacePair);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }, airbyteStreamNameNamespacePair);
  }

  public static void logStreamSyncStatus(final List<ConfiguredAirbyteStream> streams, final String syncType) {
    if (streams.isEmpty()) {
      LOGGER.info("No Streams will be synced via {}.", syncType);
    } else {
      LOGGER.info("Streams to be synced via {} : {}", syncType, streams.size());
      LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(streams));
    }
  }

  public static String prettyPrintConfiguredAirbyteStreamList(final List<ConfiguredAirbyteStream> streamList) {
    return streamList.stream().map(s -> "%s.%s".formatted(s.getStream().getNamespace(), s.getStream().getName())).collect(Collectors.joining(", "));
  }

}
