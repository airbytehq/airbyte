/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.SqlDatabase;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.List;
import java.util.StringJoiner;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class for methods to query a relational db.
 */
public class RelationalDbQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(RelationalDbQueryUtils.class);

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

  public static <Database extends SqlDatabase> AutoCloseableIterator<JsonNode> queryTable(final Database database, final String sqlQuery,
      final String tableName, final String schemaName) {
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

}
