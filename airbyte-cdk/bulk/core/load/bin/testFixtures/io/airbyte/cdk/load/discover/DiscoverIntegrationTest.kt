/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discover

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.protocol.models.v0.AirbyteMessage
import kotlin.test.assertEquals
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

data class DiscoverTestConfig(
    val configContents: String,
    val featureFlags: Set<FeatureFlag> = emptySet(),
    val name: String? = null,
)

abstract class DiscoverIntegrationTest<T : ConfigurationSpecification>(
    val successConfigFilenames: List<DiscoverTestConfig>,
    additionalMicronautEnvs: List<String> = emptyList(),
    micronautProperties: Map<Property, String> = emptyMap(),
    configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        configUpdater = configUpdater,
        micronautProperties = micronautProperties,
    ) {
    @Test
    open fun testSuccessConfigs() {
        for (tc in successConfigFilenames) {
            val updatedConfig = updateConfig(tc.configContents)
            val process =
                destinationProcessFactory.createDestinationProcess(
                    "discover",
                    configContents = updatedConfig,
                    featureFlags = tc.featureFlags.toTypedArray(),
                    micronautProperties = micronautProperties,
                )
            runBlocking { process.run() }
            val messages = process.readMessages()
            val catalogMessages =
                messages.filter { it.type == AirbyteMessage.Type.DESTINATION_CATALOG }
            val testName = tc.name ?: ""

            assertEquals(
                catalogMessages.size,
                1,
                "$testName: Expected to receive exactly one destination catalog message, but got ${catalogMessages.size}: $catalogMessages"
            )
            assertFalse(
                catalogMessages.first().destinationCatalog.operations.isEmpty(),
                "$testName: Catalogs is expected to have at least one operation"
            )
        }
    }
}
