/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2

import io.airbyte.integrations.source.cdk.AbstractSourceCheckIntegrationTest
import io.airbyte.integrations.source.cdk.NamespacedContainer
import io.airbyte.integrations.source.db2.config.Db2ContainerFactory
import io.airbyte.integrations.source.db2.config.Db2SourceConfigurationFactory
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.Db2Container

class Db2SourceCheckIntegrationTest : AbstractSourceCheckIntegrationTest() {

    private val configSpec = Db2ContainerFactory.configSpecification(namespacedContainer)

    override val testCases =
        listOf(TestCase("vanilla", configSpec, Db2SourceConfigurationFactory().make(configSpec)))

    companion object {
        lateinit var namespacedContainer: NamespacedContainer<Db2Container>

        @BeforeAll
        @JvmStatic
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            namespacedContainer = Db2ContainerFactory.shared(this::class)
        }
    }
}
