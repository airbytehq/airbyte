/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName

object PostgresContainerFactory {
    const val COMPATIBLE_NAME = "postgres:15-alpine"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::PostgreSQLContainer)
    }

    sealed interface PostgresContainerModifier :
        TestContainerFactory.ContainerModifier<PostgreSQLContainer<*>>

    fun exclusive(
        imageName: String,
        vararg modifiers: PostgresContainerModifier,
    ): PostgreSQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: PostgresContainerModifier,
    ): PostgreSQLContainer<*> {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun config(postgresContainer: PostgreSQLContainer<*>): PostgresV2SourceConfigurationSpecification =
        PostgresV2SourceConfigurationSpecification().apply {
            host = postgresContainer.host
            port = postgresContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
            username = postgresContainer.username
            password = postgresContainer.password
            database = postgresContainer.databaseName
            schemas = listOf("public")
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
            setIncrementalValue(UserDefinedCursor)
        }
}
