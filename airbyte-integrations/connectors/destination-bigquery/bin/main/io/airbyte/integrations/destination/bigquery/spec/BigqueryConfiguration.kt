/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.write.db.DbConstants
import jakarta.inject.Singleton

data class BigqueryConfiguration(
    val projectId: String,
    val datasetLocation: BigqueryRegion,
    val datasetId: String,
    val loadingMethod: LoadingMethodConfiguration,
    val credentialsJson: String?,
    val cdcDeletionMode: CdcDeletionMode,
    val internalTableDataset: String,
    val legacyRawTablesOnly: Boolean,
) : DestinationConfiguration() {
    override val numOpenStreamWorkers = 3
    // currently the base cdk declares 0.2 as the default.
    // use 0.4 so that we support 20MiB records.
    override val maxMessageQueueMemoryUsageRatio = 0.4
}

sealed interface LoadingMethodConfiguration

data object BatchedStandardInsertConfiguration : LoadingMethodConfiguration

data class GcsStagingConfiguration(
    val gcsClientConfig: GcsClientConfiguration,
    val filePostProcessing: GcsFilePostProcessing,
) : LoadingMethodConfiguration

@Singleton
class BigqueryConfigurationFactory :
    DestinationConfigurationFactory<BigquerySpecification, BigqueryConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: BigquerySpecification): BigqueryConfiguration {
        val loadingMethodConfig =
            when (pojo.loadingMethod) {
                is GcsStagingSpecification -> {
                    val gcsStagingSpec = pojo.loadingMethod as GcsStagingSpecification
                    GcsStagingConfiguration(
                        GcsClientConfiguration(gcsStagingSpec, pojo.datasetLocation.gcsRegion),
                        gcsStagingSpec.filePostProcessing ?: GcsFilePostProcessing.DELETE,
                    )
                }
                is BatchedStandardInsertSpecification,
                null -> BatchedStandardInsertConfiguration
            }
        return BigqueryConfiguration(
            projectId = pojo.projectId,
            pojo.datasetLocation,
            datasetId = pojo.datasetId,
            loadingMethodConfig,
            credentialsJson = pojo.credentialsJson,
            // default to hard delete for backwards compatibility.
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
            internalTableDataset =
                if (pojo.internalTableDataset.isNullOrBlank()) {
                    DbConstants.DEFAULT_RAW_TABLE_NAMESPACE
                } else {
                    pojo.internalTableDataset!!
                },
            legacyRawTablesOnly = pojo.legacyRawTablesOnly ?: false,
        )
    }
}
