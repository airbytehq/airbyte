/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.azure.storage.blob.BlobContainerClient
import com.azure.storage.blob.BlobContainerClientBuilder
import com.azure.storage.common.StorageSharedKeyCredential
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.setOnce
import java.util.concurrent.atomic.AtomicBoolean
import org.testcontainers.azure.AzuriteContainer
import org.testcontainers.utility.DockerImageName

object AzureBlobStorageTestContainer {
    private const val ACCOUNT_NAME = "devstoreaccount1"
    private const val CONTAINER_NAME = "container-name"

    private val container =
        AzuriteContainer(DockerImageName.parse("mcr.microsoft.com/azure-storage/azurite:3.33.0"))
    private val hasStarted = AtomicBoolean(false)

    fun start() {
        if (hasStarted.setOnce()) {
            container.start()
            client.serviceClient.createBlobContainer(CONTAINER_NAME)
        }
    }
    // intentionally no stop method - testcontainers automatically stop when their parent java
    // process exits (via ryuk)

    private val endpointUrl
        get() = "http://${container.host}:${container.firstMappedPort}/$ACCOUNT_NAME"

    // TODO return an actual object, this is copied out of old code
    val config: Any
        get() {
            val stubFormatConfig = Jsons.createObjectNode()
            stubFormatConfig.put("file_extension", java.lang.Boolean.TRUE)
            val stubConfig = Jsons.createObjectNode()
            stubConfig.set<ObjectNode>("format", stubFormatConfig)

            /*return*/ listOf(
                endpointUrl,
                "devstoreaccount1",
                "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
                "container-name",
                1, // output stream buffer size - probably want to kill this (or at least rely on
                // our application-test.yaml microbatching thing)
                1, // blob spill size - we can probably leave this unconfigured???
                stubConfig,
            )
            return TODO()
        }

    val client: BlobContainerClient
        get() {
            val credential =
                StorageSharedKeyCredential(
                    ACCOUNT_NAME,
                    // TODO where did this magic value come from?
                    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
                )

            return BlobContainerClientBuilder()
                .endpoint(endpointUrl)
                .credential(credential)
                .containerName(CONTAINER_NAME)
                .buildClient()
        }
}
