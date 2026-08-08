/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

/**
 * Snowflake data types for use in SQL DDL statements. These correspond to Snowflake's native SQL
 * data types.
 */
enum class SnowflakeDataType(val typeName: String) {
    // Number is being used for numbers with scale 0.
    NUMBER("NUMBER"),
    // NUMERIC - synonym for NUMBER in Snowflake. Used for numbers with scale > 0. A column created
    // as NUMERIC(38, 9) is
    // stored as NUMBER(38,9), what DESCRIBE TABLE returns.
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
