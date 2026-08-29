/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.sql

/** Firebolt data type names for use in SQL DDL. */
enum class FireboltDataType(val typeName: String) {
    BOOLEAN("boolean"),
    BIGINT("bigint"),
    INTEGER("int"),
    REAL("real"),
    DOUBLE_PRECISION("double precision"),
    NUMERIC("numeric(38,9)"),
    TEXT("text"),
    BYTEA("bytea"),
    DATE("date"),
    TIMESTAMP("timestamp"),
    TIMESTAMPTZ("timestamptz"),
    JSON("json"),
    GEOGRAPHY("geography"),
}
