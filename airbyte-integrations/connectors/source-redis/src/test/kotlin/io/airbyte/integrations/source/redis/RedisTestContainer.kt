/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import org.testcontainers.containers.GenericContainer
import org.testcontainers.utility.DockerImageName

class RedisTestContainer(
    image: DockerImageName = DockerImageName.parse("redis:8"),
) : GenericContainer<RedisTestContainer>(image)
