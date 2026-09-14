/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

/**
 * Snowflake data types for use in SQL DDL statements. These correspond to Snowflake's native SQL
 * data types.
 */
enum class SnowflakeDataType(val typeName: String) {
    // Number is being used for Integers i.e. numbers with scale 0. Defaults to NUMBER(38,0)
    NUMBER("NUMBER"),
    NUMERIC_38_9("NUMERIC(38,9)"),
    FLOAT("FLOAT"),

    // String & binary types
    VARCHAR("VARCHAR"),

    // Boolean type
    BOOLEAN("BOOLEAN"),

    // Date & time types
    DATE("DATE"),
    TIME("TIME"),
    TIMESTAMP_NTZ("TIMESTAMP_NTZ"),
    TIMESTAMP_TZ("TIMESTAMP_TZ"),

    // Semi-structured types
    ARRAY("ARRAY"),
    OBJECT("OBJECT"),
    VARIANT("VARIANT"),
}
