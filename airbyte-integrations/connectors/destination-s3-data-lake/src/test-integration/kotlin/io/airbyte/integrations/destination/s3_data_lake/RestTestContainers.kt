/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.util.setOnce
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean
import org.testcontainers.containers.ComposeContainer

/**
 * Shared test containers for all Rest catalog tests, so that we don't launch redundant docker
 * containers
 */
object RestTestContainers {
    val composeFile = File("src/test-integration/resources/rest/docker-compose.yml")
    val testcontainers: ComposeContainer =
        ComposeContainer(composeFile)
            .withExposedService("minio", 9000)
            .withExposedService("rest", 8181)
            // we don't directly interact with spark,
            // but this container depends on minio+rest,
            // so it's an easy proxy for everything being started.
            .withExposedService("spark-iceberg", 8080)
    private val startRestContainerRunOnce = AtomicBoolean(false)

    /**
     * Start the test containers, or if another thread already called this method, wait for them to
     * finish starting
     */
    fun start() {
        if (startRestContainerRunOnce.setOnce()) {
            testcontainers.start()
        } else {
            // afaict there's no method to wait for the containers to start
            // so just poll until these methods stop throwing exceptions
            while (true) {
                try {
                    testcontainers.getServicePort("spark-iceberg", 8080)
                } catch (e: IllegalStateException) {
                    // do nothing
                }
                break
            }
        }
    }

    // intentionally no stop method - testcontainers automatically stop when their parent java
    // process exits (via ryuk)
}
