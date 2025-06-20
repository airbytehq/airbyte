/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Property
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private const val TEST_CONFIG =
    """
    {
        "objectStorageConfig":{
            "storage_type":"None"
        }
    }
"""

@Property(name = "airbyte.connector.config.json", value = TEST_CONFIG)
@Property(name = "airbyte.connector.catalog.resource", value = "dlq-catalog.json")
@Property(name = "airbyte.connector.operation", value = "write")
@MicronautTest(rebuildContext = true, startApplication = false)
class NoDeadLetterQueueMicronautTest {

    // Sets the test to an object loader test
    @MockBean(ObjectLoader::class)
    val objectloader =
        object : ObjectLoader {
            override val inputPartitions = 1
            override val numPartWorkers = 1
        }

    @Inject lateinit var objectStorageConfig: ObjectStorageConfig

    @Named("dlqPipelineSteps") @Inject lateinit var pipelineSteps: List<LoadPipelineStep>

    @Test
    fun `verify the configuration is the DisabledObjectStorageConfig`() {
        assertEquals(DisabledObjectStorageConfig::class, objectStorageConfig::class)
    }

    @Test
    fun `verify the dlqPipelineSteps are empty`() {
        assertEquals(0, pipelineSteps.size)
    }
}
