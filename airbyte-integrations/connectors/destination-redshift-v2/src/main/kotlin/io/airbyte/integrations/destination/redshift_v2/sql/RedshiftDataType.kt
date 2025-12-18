/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.sql

/** Redshift data types. Redshift is PostgreSQL-based but has some differences in type support. */
enum class RedshiftDataType(val typeName: String) {
    // String types
    VARCHAR("VARCHAR(65535)"), // Max VARCHAR length in Redshift

    // Numeric types
    BIGINT("BIGINT"),
    DOUBLE("DOUBLE PRECISION"),
    DECIMAL("DECIMAL(38, 9)"),

    // Boolean type
    BOOLEAN("BOOLEAN"),

    // Temporal types
    DATE("DATE"),
    TIME("TIME"),
    TIMESTAMP("TIMESTAMP"),
    TIMESTAMPTZ("TIMESTAMPTZ"),

    // Semi-structured type (Redshift uses SUPER for JSON)
    SUPER("SUPER"),
}
