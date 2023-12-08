/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.util.LinkedHashMap;

/**
 * Jdbc destination table definition representation
 *
 * @param columns
 */
public record TableDefinition(LinkedHashMap<String, ColumnDefinition> columns) {

}
