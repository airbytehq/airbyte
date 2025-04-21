/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.write.db.DbConstants
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class BigqueryConfiguration(
    val projectId: String,
    val datasetLocation: BigqueryRegion,
    val datasetId: String,
    val loadingMethod: LoadingMethodConfiguration,
    val credentialsJson: String?,
    val transformationPriority: TransformationPriority,
    val rawTableDataset: String,
    val disableTypingDeduping: Boolean,
) : DestinationConfiguration()

sealed interface LoadingMethodConfiguration

data object BatchedStandardInsertConfiguration : LoadingMethodConfiguration

data object BulkLoadConfiguration : LoadingMethodConfiguration

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
            pojo.transformationPriority ?: TransformationPriority.INTERACTIVE,
            rawTableDataset = pojo.rawTableDataset ?: DbConstants.DEFAULT_RAW_TABLE_NAMESPACE,
            disableTypingDeduping = pojo.disableTypingDeduping ?: false,
        )
    }
}

@Factory
class BigqueryConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton fun get() = config as BigqueryConfiguration
}
