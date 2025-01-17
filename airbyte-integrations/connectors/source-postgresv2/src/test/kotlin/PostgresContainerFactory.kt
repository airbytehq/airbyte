package io.airbyte.integrations.source.postgresv2

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Container
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.containers.Network
import org.testcontainers.utility.DockerImageName

object PostgresContainerFactory {
    const val COMPATIBLE_NAME = "postgres"
    private val log = KotlinLogging.logger {}


    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::PostgreSQLContainer)
    }

    sealed interface PostgresContainerModifier :
        TestContainerFactory.ContainerModifier<PostgreSQLContainer<*>>

    data object WithNetwork : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }
    
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
    fun config(PostgresContainer: PostgreSQLContainer<*>): PostgresV2SourceConfigurationSpecification =
        PostgresV2SourceConfigurationSpecification().apply {
            host = PostgresContainer.host
            port = PostgresContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
            username = PostgresContainer.username
            password = PostgresContainer.password
            database = "test"
        }

    fun PostgreSQLContainer<*>.exec(sql: String) {
        val result: Container.ExecResult =
            execInContainer("su", "-c", "psql -U test -c \""+sql+"\"")
        for (line in (result.stdout ?: "").lines()) {
            log.info { "STDOUT: $line" }
        }
        for (line in (result.stderr ?: "").lines()) {
            log.info { "STDOUT: $line" }
        }
        if (result.exitCode == 0) {
            return
        }
        log.error { "Exit code ${result.exitCode}" }
        throw RuntimeException("Failed to execute query $sql")
    }
}
