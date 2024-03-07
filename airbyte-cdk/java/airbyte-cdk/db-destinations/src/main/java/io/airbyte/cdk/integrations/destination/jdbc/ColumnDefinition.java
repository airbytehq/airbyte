/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

/**
 * Jdbc destination column definition representation
 *
 * @param name
 * @param type
 * @param columnSize
 */
public record ColumnDefinition(String name, String type, int columnSize, boolean isNullable) {

}
