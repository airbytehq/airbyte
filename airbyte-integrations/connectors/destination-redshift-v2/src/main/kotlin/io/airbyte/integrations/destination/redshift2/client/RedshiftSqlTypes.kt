/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.client

/**
 * Redshift SQL type constants used by [RedshiftSqlGenerator] for DDL generation.
 *
 * These types match the v1 Redshift destination's type mappings
 * (via JdbcSqlGenerator + RedshiftSqlGenerator).
 */
object RedshiftSqlTypes {
    /** Semi-structured data type for JSON objects, arrays, and unknown types. */
    const val SUPER = "SUPER"

    /** Maximum-length variable character type (65535 is Redshift's VARCHAR limit). */
    const val VARCHAR_MAX = "VARCHAR(65535)"

    /** Fixed-length UUID string type for _airbyte_raw_id. */
    const val VARCHAR_36 = "VARCHAR(36)"

    /** Timestamp with time zone (used for _airbyte_extracted_at). */
    const val TIMESTAMPTZ = "TIMESTAMPTZ"

    /** Timestamp without time zone. */
    const val TIMESTAMP = "TIMESTAMP"

    /** 64-bit integer (used for _airbyte_generation_id and INTEGER columns). */
    const val BIGINT = "BIGINT"

    /** Fixed-precision decimal (38 digits, 9 decimal places). */
    const val NUMERIC = "NUMERIC(38,9)"

    /** Boolean type. */
    const val BOOLEAN = "BOOLEAN"

    /** Calendar date. */
    const val DATE = "DATE"

    /** Time without time zone. */
    const val TIME = "TIME"

    /** Time with time zone. */
    const val TIMETZ = "TIMETZ"
}
