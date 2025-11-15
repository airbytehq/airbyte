/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

object MongodbContainerHelper {
    private val mongoContainer: MongoDBContainer by lazy {
        MongoDBContainer(DockerImageName.parse("mongo:7.0"))
            .withExposedPorts(27017)
            .apply {
                start()
            }
    }

    fun getConnectionString(): String {
        return mongoContainer.connectionString
    }

    fun getHost(): String {
        return mongoContainer.host
    }

    fun getPort(): Int {
        return mongoContainer.getMappedPort(27017)
    }

    fun getContainer(): MongoDBContainer {
        return mongoContainer
    }
}
