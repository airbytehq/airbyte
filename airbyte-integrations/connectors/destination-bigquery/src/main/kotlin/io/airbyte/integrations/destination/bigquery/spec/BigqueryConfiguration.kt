/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.write.db.DbConstants
import jakarta.inject.Singleton

data class BigqueryConfiguration(
    val projectId: String,
    val jobProjectId: String,
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
            when (val loadingMethod = pojo.loadingMethod) {
                is GcsStagingSpecification ->
                    GcsStagingConfiguration(
                        GcsClientConfiguration(loadingMethod, pojo.datasetLocation.gcsRegion),
                        loadingMethod.filePostProcessing ?: GcsFilePostProcessing.DELETE,
                    )
                is BatchedStandardInsertSpecification,
                null -> BatchedStandardInsertConfiguration
            }
        return BigqueryConfiguration(
            projectId = pojo.projectId,
            jobProjectId = pojo.jobProjectId?.takeUnless(String::isBlank) ?: pojo.projectId,
            pojo.datasetLocation,
            datasetId = pojo.datasetId,
            loadingMethodConfig,
            credentialsJson = pojo.credentialsJson,
            // default to hard delete for backwards compatibility.
            cdcDeletionMode = pojo.cdcDeletionMode ?: CdcDeletionMode.HARD_DELETE,
            internalTableDataset =
                pojo.internalTableDataset?.takeUnless(String::isBlank)
                    ?: DbConstants.DEFAULT_RAW_TABLE_NAMESPACE,
            legacyRawTablesOnly = pojo.legacyRawTablesOnly ?: false,
        )
    }
}
