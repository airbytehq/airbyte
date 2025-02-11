package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.util.setOnce
import org.testcontainers.containers.ComposeContainer
import org.testcontainers.containers.wait.strategy.Wait
import java.io.File
import java.time.Duration
import java.util.concurrent.atomic.AtomicBoolean

object RestTestContainers {

    private val composeFile = File("src/test-integration/resources/rest/docker-compose.yml")

    /**
     * Define the docker-compose services and their wait strategies so that Testcontainers
     * won't consider the environment "started" until these ports are truly available.
     */
    val testcontainers: ComposeContainer = ComposeContainer(composeFile)
        // Wait.forListeningPort() ensures Testcontainers waits until the container is actually listening.
        .withExposedService("minio", 9000, Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60)))
        .withExposedService("rest", 8181, Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60)))
        // We don't directly interact with spark here, but spark-iceberg depends on minio+rest.
        .withExposedService("spark-iceberg", 8080, Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60)))

    private val startRestContainerRunOnce = AtomicBoolean(false)

    /**
     * Start the test containers, or if another thread/class already started them, do nothing.
     * Because we added wait strategies above, this call will block until all services are actually up.
     */
    fun start() {
        if (startRestContainerRunOnce.setOnce()) {
            testcontainers.start()
        }
        // If they've already started, we don't need to do anything else.
    }
}
