package io.airbyte.cdk.integrations.destination.jdbc;

import java.util.LinkedHashMap;

/**
 * Jdbc destination table definition representation
 * @param columns
 */
public record TableDefinition(LinkedHashMap<String, ColumnDefinition> columns) {

}
