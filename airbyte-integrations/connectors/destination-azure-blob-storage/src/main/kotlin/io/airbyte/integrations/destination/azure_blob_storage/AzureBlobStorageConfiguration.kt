/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.azureBlobStorage.GENERATION_ID_METADATA_KEY_OVERRIDE
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

private const val DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.4
private const val FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.2

class AzureBlobStorageConfiguration<T : OutputStream>(
    // Client-facing configuration
    override val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    // User-configurable path and filename patterns
    private val pathFormat: String? = null,
    private val fileNamePattern: String? = null,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,

    // TODO remove these from config and hardcode them in AzureBlobStorageObjectLoader
    //   after we finish performance tuning
    val numPartWorkers: Int = 2,
    val numUploadWorkers: Int = 5,
    val maxMemoryRatioReservedForParts: Double = DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS,
    val objectSizeBytes: Long = 200L * 1024 * 1024,
    val partSizeBytes: Long = 10L * 1024 * 1024,
) :
    DestinationConfiguration(),
    AzureBlobStorageClientConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T> {

    companion object {
        /** Default path when user does not provide one. */
        const val DEFAULT_PATH_PATTERN = "\${NAMESPACE}/\${STREAM_NAME}/"
        /** Default file-name when user does not provide one. */
        const val DEFAULT_FILE_NAME_PATTERN = "{date}_{timestamp}_{part_number}{format_extension}"
    }

    /**
     * Normalise the user-supplied path format:
     *  - Variables may come as {VAR}, ${VAR}, or ${var}; always convert to ${VAR}.
     *  - Ensure a trailing '/'.
     *  - Fall back to the default pattern when blank.
     */
    private fun resolvePathPattern(raw: String?): String {
        val trimmed = raw?.trim()?.takeIf { it.isNotBlank() } ?: return DEFAULT_PATH_PATTERN
        // Normalise {var} / ${var} / ${VAR} → ${VAR}
        // The \$? optionally consumes an existing $ so we don't double it
        val normalised =
            trimmed.replace("""\$?\{(\w+)}""".toRegex()) { match ->
                "\${${match.groupValues[1].uppercase()}}"
            }
        return if (normalised.endsWith('/')) normalised else "$normalised/"
    }

    /**
     * Normalise the user-supplied filename pattern.
     * Falls back to the default when blank.
     */
    private fun resolveFileNamePattern(raw: String?): String {
        return raw?.trim()?.takeIf { it.isNotBlank() } ?: DEFAULT_FILE_NAME_PATTERN
    }

    override val objectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = "",
            pathPattern = resolvePathPattern(pathFormat),
            fileNamePattern = resolveFileNamePattern(fileNamePattern),
            resolveNamesMethod = { Transformations.toAzureBlobSafePath(it) },
        )

    override val generationIdMetadataKey = GENERATION_ID_METADATA_KEY_OVERRIDE
}

@Singleton
class AzureBlobStorageConfigurationFactory(private val destinationCatalog: DestinationCatalog) :
    DestinationConfigurationFactory<
        AzureBlobStorageSpecification, AzureBlobStorageConfiguration<*>> {
    override fun makeWithoutExceptionHandling(
        pojo: AzureBlobStorageSpecification
    ): AzureBlobStorageConfiguration<*> {
        val azureBlobStorageClientConfiguration = pojo.toAzureBlobStorageClientConfiguration()
        azureBlobStorageClientConfiguration.endpointDomainName =
            pojo.azureBlobStorageEndpointDomainName
        azureBlobStorageClientConfiguration.spillSize = pojo.azureBlobStorageSpillSize
        return AzureBlobStorageConfiguration(
            azureBlobStorageClientConfiguration = azureBlobStorageClientConfiguration,
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
            objectStorageCompressionConfiguration =
                ObjectStorageCompressionConfiguration(NoopProcessor),
            pathFormat = pojo.pathFormat,
            fileNamePattern = pojo.fileNamePattern,
            maxMemoryRatioReservedForParts =
                if (destinationCatalog.streams.any { it.isFileBased }) {
                    FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                } else {
                    DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                }
        )
    }
}

@Suppress("UNCHECKED_CAST")
@Factory
class AzureBlobStorageConfigurationProvider<T : OutputStream>(
    private val config: DestinationConfiguration
) {
    @Singleton
    fun get(): AzureBlobStorageConfiguration<T> {
        return config as AzureBlobStorageConfiguration<T>
    }
}
