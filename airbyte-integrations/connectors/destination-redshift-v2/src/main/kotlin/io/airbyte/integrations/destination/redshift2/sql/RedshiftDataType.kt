/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

/**
 * Redshift data types for use in SQL DDL statements. These correspond to a subset of Redshift's
 * native SQL data types.
 *
 * Used by [RedshiftTableSchemaMapper] to map Airbyte field types to Redshift column types, by
 * [RedshiftColumnManager] to define meta column types, and by [RedshiftSqlGenerator] for DDL
 * generation.
 */
enum class RedshiftDataType(val typeName: String) {
    // Numeric types
    BIGINT("bigint"),
    NUMERIC("numeric(38,9)"),

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
