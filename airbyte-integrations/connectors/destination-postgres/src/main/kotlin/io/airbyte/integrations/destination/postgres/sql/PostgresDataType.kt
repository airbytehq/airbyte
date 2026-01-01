/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

/**
 * Postgres data types for use in SQL DDL statements. These correspond to a subset of Postgres'
 * native SQL data types.
 */
enum class PostgresDataType(val typeName: String) {
    // Numeric types
    BIGINT("bigint"),
    DECIMAL("decimal"),

    // String
    VARCHAR("varchar"),

    // Boolean type
    BOOLEAN("boolean"),

    // Date & time types
    DATE("date"),
    TIME_WITH_TIMEZONE("time with time zone"),
    TIME("time"),
    TIMESTAMP_WITH_TIMEZONE("timestamp with time zone"),
    TIMESTAMP("timestamp"),

    // Semi-structured types
    JSONB("jsonb"),
}
