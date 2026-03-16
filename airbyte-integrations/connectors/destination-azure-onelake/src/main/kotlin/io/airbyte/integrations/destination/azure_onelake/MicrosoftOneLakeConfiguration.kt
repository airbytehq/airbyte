/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_onelake

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
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.io.OutputStream

private const val DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.4
private const val FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.2

/**
 * Runtime configuration for the Microsoft OneLake destination.
 *
 * OneLake ABFS URI structure:
 *   abfss://<workspaceName>@onelake.dfs.fabric.microsoft.com/<item>.<itemtype>/Files/<subPath>/<pathPattern>
 *
 * This is achieved by:
 *  - endpoint  = "onelake.dfs.fabric.microsoft.com"   (fixed)
 *  - account   = workspaceName / GUID
 *  - container = "<ItemName>.<ItemType>"  e.g. "MyLakehouse.Lakehouse"
 *  - prefix    = "Files/<oneLakeFilesSubPath>/"        (prepended to every object key)
 *  - pathPattern / fileNamePattern apply on top of prefix as usual
 */
class MicrosoftOneLakeConfiguration<T : OutputStream>(
    override val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    private val pathFormat: String? = null,
    private val fileNamePattern: String? = null,

    /** Sub-path inside the Lakehouse 'Files/' section. Defaults to "airbyte". */
    val oneLakeFilesSubPath: String = "airbyte",

    /** OneLake item path segment e.g. "MyLakehouse.Lakehouse" (used in blob path prefix). */
    private val oneLakeItemPath: String = "Lakehouse.Lakehouse",

    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,

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
        const val DEFAULT_PATH_PATTERN = "\${NAMESPACE}/\${STREAM_NAME}/"
        const val DEFAULT_FILE_NAME_PATTERN = "{date}_{timestamp}_{part_number}{format_extension}"
        const val ONELAKE_FILES_ROOT = "Files"
    }

    /**
     * Normalise path-pattern variables to the \${VAR} form expected by the CDK,
     * and ensure a trailing '/'.
     */
    private fun resolvePathPattern(raw: String?): String {
        val trimmed = raw?.trim()?.takeIf { it.isNotBlank() } ?: return DEFAULT_PATH_PATTERN
        val normalised = trimmed.replace("""\$?\{(\w+)}""".toRegex()) { match ->
            "\${${match.groupValues[1].uppercase()}}"
        }
        return if (normalised.endsWith('/')) normalised else "$normalised/"
    }

    private fun resolveFileNamePattern(raw: String?): String =
        raw?.trim()?.takeIf { it.isNotBlank() } ?: DEFAULT_FILE_NAME_PATTERN

    /**
     * Build the blob path prefix. OneLake uses container=workspace, path=item.itemtype/Files/...
     * Full path: <oneLakeItemPath>/Files/<oneLakeFilesSubPath>/${NAMESPACE}/${STREAM_NAME}/
     */
    private fun buildPrefix(): String {
        val item = oneLakeItemPath.trim().trimEnd('/')
        val sub = oneLakeFilesSubPath.trim().trimStart('/').trimEnd('/')
        val filesPart = if (sub.isBlank()) "$ONELAKE_FILES_ROOT/" else "$ONELAKE_FILES_ROOT/$sub/"
        return if (item.isBlank()) filesPart else "$item/$filesPart"
    }

    override val objectStoragePathConfiguration = ObjectStoragePathConfiguration(
        prefix = buildPrefix(),
        pathPattern = resolvePathPattern(pathFormat),
        fileNamePattern = resolveFileNamePattern(fileNamePattern),
        resolveNamesMethod = { Transformations.toAzureBlobSafePath(it) },
    )

    override val generationIdMetadataKey = GENERATION_ID_METADATA_KEY_OVERRIDE
}

@Singleton
@Primary
class MicrosoftOneLakeConfigurationFactory(
    private val destinationCatalog: DestinationCatalog
) : DestinationConfigurationFactory<MicrosoftOneLakeSpecification, MicrosoftOneLakeConfiguration<*>> {

    override fun makeWithoutExceptionHandling(
        pojo: MicrosoftOneLakeSpecification
    ): MicrosoftOneLakeConfiguration<*> {

        val rawLakehouse = pojo.azureBlobStorageContainerName.trim()
        // OneLake path segment must be {itemname}.{itemtype} e.g. mylakehouse.Lakehouse
        val oneLakeItemPath =
            if (rawLakehouse.contains(".")) rawLakehouse
            else "$rawLakehouse.Lakehouse"

        // OneLake Blob API: container = workspace, blob path = item.itemtype/Files/subPath/...
        val clientConfig = pojo.toAzureBlobStorageClientConfiguration().apply {
            endpointUrl = "https://onelake.blob.fabric.microsoft.com"
            spillSize = pojo.azureBlobStorageSpillSize
        }.copy(
            containerName = pojo.azureBlobStorageAccountName
        )

        // Guard: require Service Principal only when not using Managed Identity
        if (!pojo.useManagedIdentity) {
            require(!pojo.azureTenantId.isNullOrBlank()) {
                "Microsoft OneLake requires Azure Tenant ID when not using Managed Identity. You can locate your tenant id at https://learn.microsoft.com/partner-center/find-ids-and-domain-names"
            }
            require(!pojo.azureClientId.isNullOrBlank()) {
                "Microsoft OneLake requires Azure Client ID when not using Managed Identity."
            }
            require(!pojo.azureClientSecret.isNullOrBlank()) {
                "Microsoft OneLake requires Azure Client Secret when not using Managed Identity."
            }
        }

        return MicrosoftOneLakeConfiguration(
            azureBlobStorageClientConfiguration = clientConfig,
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
            objectStorageCompressionConfiguration =
                ObjectStorageCompressionConfiguration(NoopProcessor),
            pathFormat = pojo.pathFormat,
            fileNamePattern = pojo.fileNamePattern,
            oneLakeFilesSubPath = pojo.oneLakeFilesSubPath?.takeIf { it.isNotBlank() } ?: "data",
            oneLakeItemPath = oneLakeItemPath,
            maxMemoryRatioReservedForParts =
                if (destinationCatalog.streams.any { it.isFileBased })
                    FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                else
                    DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
        )
    }
}

@Suppress("UNCHECKED_CAST")
@Factory
class MicrosoftOneLakeConfigurationProvider<T : OutputStream>(
    private val config: DestinationConfiguration
) {
    @Singleton
    fun get(): MicrosoftOneLakeConfiguration<T> = config as MicrosoftOneLakeConfiguration<T>
}