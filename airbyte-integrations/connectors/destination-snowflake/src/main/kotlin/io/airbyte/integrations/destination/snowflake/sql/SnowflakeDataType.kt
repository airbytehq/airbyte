/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

/**
 * Snowflake data types for use in SQL DDL statements. These correspond to Snowflake's native SQL
 * data types.
 */
enum class SnowflakeDataType(val typeName: String) {
    // Numeric types
    NUMBER("NUMBER"),
    DECIMAL("DECIMAL"),
    NUMERIC("NUMERIC"),
    INT("INT"),
    INTEGER("INTEGER"),
    BIGINT("BIGINT"),
    SMALLINT("SMALLINT"),
    TINYINT("TINYINT"),
    BYTEINT("BYTEINT"),
    FLOAT("FLOAT"),
    FLOAT4("FLOAT4"),
    FLOAT8("FLOAT8"),
    DOUBLE("DOUBLE"),
    DOUBLE_PRECISION("DOUBLE PRECISION"),
    REAL("REAL"),

    // String & binary types
    VARCHAR("VARCHAR"),
    CHAR("CHAR"),
    CHARACTER("CHARACTER"),
    STRING("STRING"),
    TEXT("TEXT"),
    BINARY("BINARY"),
    VARBINARY("VARBINARY"),

    // Boolean type
    BOOLEAN("BOOLEAN"),

    // Date & time types
    DATE("DATE"),
    DATETIME("DATETIME"),
    TIME("TIME"),
    TIMESTAMP("TIMESTAMP"),
    TIMESTAMP_LTZ("TIMESTAMP_LTZ"),
    TIMESTAMP_NTZ("TIMESTAMP_NTZ"),
    TIMESTAMP_TZ("TIMESTAMP_TZ"),

    // Semi-structured types
    VARIANT("VARIANT"),
    OBJECT("OBJECT"),
    ARRAY("ARRAY"),

    // Geospatial types
    GEOGRAPHY("GEOGRAPHY"),
    GEOMETRY("GEOMETRY"),

    // Vector type (added in 2024)
    VECTOR("VECTOR")
}
