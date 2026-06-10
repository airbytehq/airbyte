/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.sql

/** Redshift data types for use in SQL DDL statements */
enum class RedshiftDataType(val typeName: String) {
    // Numeric types
    BIGINT("bigint"),
    NUMERIC("decimal(38,9)"),

    // String types
    VARCHAR("varchar(65535)"),
    VARCHAR_36("varchar(36)"),

    // Boolean type
    BOOLEAN("boolean"),

    // Date & time types
    DATE("date"),
    TIME("time"),
    TIMETZ("timetz"),
    TIMESTAMP("timestamp"),
    TIMESTAMPTZ("timestamptz"),

    // Semi-structured type
    SUPER("super"),
}
