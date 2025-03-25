/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.azure.core.util.BinaryData
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class AzureBlobStorageDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val blobs =
            AzureBlobStorageTestContainer.client.listBlobsByHierarchy(
                "${stream.descriptor.namespace}/${stream.descriptor.name}"
            )
        return emptyList()
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        TODO("Not yet implemented")
    }
}

class X {
    @Test
    fun arst() {
        val storageClient = AzureBlobStorageTestContainer.client
        val blobClient = storageClient.getBlobClient("namespace/name")
        blobClient.blockBlobClient.upload(
            BinaryData.fromBytes("file contents".toByteArray(Charsets.UTF_8))
        )
        println()
    }

    companion object {
        @BeforeAll
        @JvmStatic
        fun setup() {
            AzureBlobStorageTestContainer.start()
        }
    }
}
