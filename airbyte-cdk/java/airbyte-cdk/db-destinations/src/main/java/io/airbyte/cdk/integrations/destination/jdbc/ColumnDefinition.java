/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.sql.SQLType;

public record ColumnDefinition(String name, String type, SQLType sqlType, int columnSize) {

}
