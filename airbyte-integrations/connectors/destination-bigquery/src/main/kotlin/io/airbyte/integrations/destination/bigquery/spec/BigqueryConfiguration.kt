/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.ConfigErrorException
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
    val streamConfigurations: Map<StreamSelector, BigqueryStreamConfiguration>,
) : DestinationConfiguration() {
    override val numOpenStreamWorkers = 3
    // currently the base cdk declares 0.2 as the default.
    // use 0.4 so that we support 20MiB records.
    override val maxMessageQueueMemoryUsageRatio = 0.4
}

data class StreamSelector(val namespace: String?, val name: String)

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
        val streamConfigurations = pojo.streamConfigurations.orEmpty()
        streamConfigurations.forEach(::validateStreamConfiguration)
        val duplicateSelectors =
            streamConfigurations
                .groupingBy { StreamSelector(it.streamNamespace, it.streamName) }
                .eachCount()
                .filterValues { it > 1 }
                .keys
        if (duplicateSelectors.isNotEmpty()) {
            throw ConfigErrorException(
                "Duplicate BigQuery stream configurations: ${duplicateSelectors.joinToString()}",
            )
        }

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
            streamConfigurations =
                streamConfigurations.associateBy {
                    StreamSelector(it.streamNamespace, it.streamName)
                },
        )
    }

    private fun validateStreamConfiguration(stream: BigqueryStreamConfiguration) {
        if (stream.streamName.isBlank()) {
            throw ConfigErrorException("BigQuery stream configuration requires a stream name.")
        }
        if (stream.streamNamespace?.isBlank() == true) {
            throw ConfigErrorException(
                "Stream ${stream.streamName}: stream namespace cannot be blank.",
            )
        }
        if (stream.destinationDataset?.isBlank() == true) {
            throw ConfigErrorException(
                "Stream ${stream.streamName}: destination dataset cannot be blank.",
            )
        }
        if (stream.destinationTable?.isBlank() == true) {
            throw ConfigErrorException(
                "Stream ${stream.streamName}: destination table cannot be blank.",
            )
        }
        if (stream.partitioningField?.isBlank() == true) {
            throw ConfigErrorException(
                "Stream ${stream.streamName}: partitioning field cannot be blank.",
            )
        }
        if (stream.partitioningGranularity != null && stream.partitioningField == null) {
            throw ConfigErrorException(
                "Stream ${stream.streamName}: partitioning granularity requires a partitioning field.",
            )
        }
        stream.clusteringFields?.let { fields ->
            if (fields.isEmpty() || fields.size > 4 || fields.any { it.isBlank() }) {
                throw ConfigErrorException(
                    "Stream ${stream.streamName}: clustering_fields must contain one to four non-blank field names.",
                )
            }
            if (fields.distinctBy { it.lowercase() }.size != fields.size) {
                throw ConfigErrorException(
                    "Stream ${stream.streamName}: clustering_fields cannot contain duplicates.",
                )
            }
        }
    }
}
