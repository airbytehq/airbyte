/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.config

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.integrations.source.cdk.NamespacedContainer
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.reflect.KClass
import org.testcontainers.containers.Db2Container
import org.testcontainers.utility.DockerImageName

object Db2ContainerFactory {
    private val log = KotlinLogging.logger {}
    private val IMAGE_NAME = DockerImageName.parse("icr.io/db2_community/db2")

    init {
        TestContainerFactory.register(IMAGE_NAME, Db2ContainerFactory::LicensedContainer)
    }

    // This constructor allows us to accept an EULA required by the IBM Db2 image.
    // See the "EULA Acceptance" section in the Testcontainers docs for more info:
    // https://java.testcontainers.org/modules/databases/db2/
    private class LicensedContainer(dockerImageName: DockerImageName) :
        Db2Container(dockerImageName) {
        init {
            this.acceptLicense()
        }
    }

    fun shared(testClass: KClass<*>): NamespacedContainer<Db2Container> {
        return NamespacedContainer(TestContainerFactory.shared(IMAGE_NAME), testClass)
    }

    @JvmStatic
    fun configSpecification(
        namespacedContainer: NamespacedContainer<Db2Container>
    ): Db2SourceConfigurationSpecification =
        Db2SourceConfigurationSpecification().apply {
            host = namespacedContainer.container.host
            port = namespacedContainer.container.firstMappedPort
            database = namespacedContainer.container.databaseName
            username = namespacedContainer.container.username
            password = namespacedContainer.container.password
            jdbcUrlParams = ""
            schemas = listOf(namespacedContainer.namespace)
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
        }
}
