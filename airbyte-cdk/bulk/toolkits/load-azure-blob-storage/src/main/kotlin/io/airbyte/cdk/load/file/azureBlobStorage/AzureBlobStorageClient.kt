/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.azureBlobStorage

import com.azure.core.util.BinaryData
import com.azure.storage.blob.BlobServiceClient
import com.azure.storage.blob.models.BlobStorageException
import com.azure.storage.blob.models.ListBlobsOptions
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import java.io.InputStream
import java.time.OffsetDateTime
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/** Represents a single blob in Azure. */
data class AzureBlob(
    override val key: String,
    override val storageConfig: AzureBlobStorageConfiguration
) : RemoteObject<AzureBlobStorageConfiguration>

class AzureBlobClient(
    private val serviceClient: BlobServiceClient,
    private val blobConfig: AzureBlobStorageConfiguration
) : ObjectStorageClient<AzureBlob> {

    /** List all blobs that start with [prefix]. We emit them as a Flow. */
    override suspend fun list(prefix: String): Flow<AzureBlob> = flow {
        val containerClient = serviceClient.getBlobContainerClient(blobConfig.containerName)

        containerClient
            .listBlobs(ListBlobsOptions().setPrefix(prefix), null)
            .map { it.name }
            .filter { it.startsWith(prefix) }
            .forEach { emit(AzureBlob(it, blobConfig)) }
    }

    /** Move is not a single operation in Azure; we have to do a copy + delete. */
    override suspend fun move(remoteObject: AzureBlob, toKey: String): AzureBlob {
        return move(remoteObject.key, toKey)
    }

    override suspend fun move(key: String, toKey: String): AzureBlob {
        val sourceBlob =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)

        val destBlob =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(toKey)

        // Start copy
        val copyResp = destBlob.beginCopy(sourceBlob.blobUrl, null)

        copyResp.waitForCompletion()

        // Delete source
        sourceBlob.delete()
        return AzureBlob(toKey, blobConfig)
    }

    /** Fetch the blob as an InputStream, pass it to [block]. */
    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        val blobClient =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)

        blobClient.openInputStream().use { inputStream ->
            return block(inputStream)
        }
    }

    /** Returns the user-defined metadata on the blob. */
    override suspend fun getMetadata(key: String): Map<String, String> {
        val blobClient =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)

        val props = blobClient.properties
        // The Azure SDK has "metadata" as a Map<String,String>.
        // If the blob doesn't exist, this can throw.
        return props?.metadata ?: emptyMap()
    }

    suspend fun getProperties(key: String): OffsetDateTime? {
        val blobClient =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)

        val props = blobClient.properties
        // The Azure SDK has "metadata" as a Map<String,String>.
        // If the blob doesn't exist, this can throw.
        return props?.creationTime
    }

    /** Upload a small byte array in a single shot. */
    override suspend fun put(key: String, bytes: ByteArray): AzureBlob {
        val blobClient =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)

        blobClient.upload(BinaryData.fromBytes(bytes), true)
        return AzureBlob(key, blobConfig)
    }

    /** Delete a blob by remoteObject */
    override suspend fun delete(remoteObject: AzureBlob) {
        delete(remoteObject.key)
    }

    /** Delete a blob by key */
    override suspend fun delete(key: String) {
        val blobClient =
            serviceClient.getBlobContainerClient(blobConfig.containerName).getBlobClient(key)
        try {
            blobClient.delete()
        } catch (e: BlobStorageException) {
            if (e.statusCode == 404) {
                // ignore not-found
            } else {
                throw e
            }
        }
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<AzureBlob> {
        val blobClient =
            serviceClient
                .getBlobContainerClient(blobConfig.containerName)
                .getBlobClient(key)
                .getBlockBlobClient()

        return AzureBlobStreamingUpload(blobClient, blobConfig, metadata)
    }
}
