/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

object MongoDbContainerFactory {

    private const val COMPATIBLE_NAME = "mongo:4.0.10"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::MongoDBContainer)
    }

    sealed interface MongoDbContainerModifier :
        TestContainerFactory.ContainerModifier<MongoDBContainer>

    data object WithNetwork : MongoDbContainerModifier {
        override fun modify(container: MongoDBContainer) {
            container.withNetwork(Network.newNetwork())
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: MongoDbContainerModifier,
    ): MongoDBContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: MongoDbContainerModifier,
    ): MongoDBContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(mongoDBContainer: MongoDBContainer): MongoDbSourceConfigurationSpecification =
        MongoDbSourceConfigurationSpecification().apply {
            databaseConfigJson =
                SelfManagedReplicaSet().apply {
                    connectionString = mongoDBContainer.connectionString
                    database = "test"
                }
        }
}
