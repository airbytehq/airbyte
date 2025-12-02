/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

data class GcsCatalogConfiguration(
    val warehouseLocation: String,
    val mainBranchName: String,
    val catalogConfiguration: GcsCatalogConfig
)

sealed interface GcsCatalogConfig

data class BigLakeCatalogConfiguration(val catalogName: String, val gcpLocation: String) :
    GcsCatalogConfig

data class PolarisCatalogConfiguration(
    val serverUri: String,
    val catalogName: String,
    val clientId: String,
    val clientSecret: String,
) : GcsCatalogConfig
