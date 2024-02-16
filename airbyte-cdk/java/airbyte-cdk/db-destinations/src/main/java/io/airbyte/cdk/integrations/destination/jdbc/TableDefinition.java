/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.util.LinkedHashMap;

/**
 * Jdbc destination table definition representation with a map of column names to column definitions
 *
 * @param columns
 */
public record TableDefinition(LinkedHashMap<String, ColumnDefinition> columns) {

}
