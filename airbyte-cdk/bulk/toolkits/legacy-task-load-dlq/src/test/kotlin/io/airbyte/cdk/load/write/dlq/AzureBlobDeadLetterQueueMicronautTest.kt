/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.load.command.dlq.AzureBlobObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Property
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Test

private const val TEST_CONFIG =
    """
    {
        "object_storage_config":{
            "storage_type":"AzureBlob",
            "azure_blob_storage_account_name":"testaccount",
            "azure_blob_storage_container_name":"rejected",
            "shared_access_signature":"sv=2021-08-06&sig=test"
        }
    }
"""

@Property(name = "airbyte.connector.config.json", value = TEST_CONFIG)
@Property(name = "airbyte.connector.catalog.resource", value = "dlq-catalog.json")
@Property(name = "airbyte.connector.operation", value = "write")
@MicronautTest(rebuildContext = true, startApplication = false)
class AzureBlobDeadLetterQueueMicronautTest {
    @MockBean(ObjectLoader::class)
    val objectLoader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    @Inject lateinit var objectStorageConfig: ObjectStorageConfig
    @Inject lateinit var objectStorageClient: ObjectStorageClient<*>
    @Named("dlqPipelineSteps") @Inject lateinit var pipelineSteps: List<LoadPipelineStep>

    @Test
    fun `Azure configuration selects Azure client and builds the pipeline without S3 config`() {
        assertInstanceOf(AzureBlobObjectStorageConfig::class.java, objectStorageConfig)
        assertInstanceOf(AzureBlobClient::class.java, objectStorageClient)
        assertEquals(3, pipelineSteps.size, pipelineSteps.toString())
    }
}
