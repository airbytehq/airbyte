/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.fasterxml.jackson.annotation.JsonValue

/** The Iceberg table format version that Airbyte creates tables at. */
enum class IcebergTableFormatVersion(
    @get:JsonValue val specValue: String,
    val formatVersion: Int,
) {
    V2("v2", 2),
    V3("v3", 3),
}
