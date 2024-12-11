/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.util.setOnce
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.DefaultAsserter.fail
import org.projectnessie.testing.nessie.NessieContainer
import org.testcontainers.containers.MinIOContainer

/**
 * Shared test containers for all nessie tests, so that we don't launch redundant docker containers
 */
object NessieTestContainers {

    //    val testcontainers: ComposeContainer =
    //        ComposeContainer(File("src/test-integration/resources/nessie/docker-compose.yml"))
    //            .withLocalCompose(true)
    //    //            .withExposedService("nessie", 19120)
    //    //            .withExposedService("minio", 9000)
    //    //            .withExposedService("keycloak", 8080)
    private val startRunOnce = AtomicBoolean(false)

    /**
     * Start the test containers, or if another thread already called this method, wait for them to
     * finish starting
     */
    fun start() {
        if (startRunOnce.setOnce()) {
            //            testcontainers.start()
            val minio =
                MinIOContainer("minio/minio:RELEASE.2023-09-04T19-57-37Z")
                    .withUserName("minioadmin")
                    .withPassword("minioadmin")
            minio.start()
            val nessieBuilder =
                NessieContainer.builder()
                    .dockerImage("ghcr.io/projectnessie/nessie:0.100.0")
                    .build()
            val nessie = nessieBuilder.createContainer()
            nessie.start()

            val nessiePort = nessie.getMappedPort(19120)
            val minioPort = minio.getMappedPort(9000)

            fail("Started nessie. Port is $nessiePort")
        }
        //        } else {
        //            // afaict there's no method to wait for the containers to start
        //            // so just poll until these methods stop throwing exceptions
        //            while (true) {
        //                try {
        //                    testcontainers.getServicePort("nessie", 19120)
        //                    testcontainers.getServicePort("minio", 9000)
        //                    testcontainers.getServicePort("keycloak", 8080)
        //                } catch (e: IllegalStateException) {
        //                    // do nothing
        //                }
        //                break
        //            }
        //        }
    }

    // intentionally no stop method - testcontainers automatically stop when their parent java
    // process exits (via ryuk)
}
