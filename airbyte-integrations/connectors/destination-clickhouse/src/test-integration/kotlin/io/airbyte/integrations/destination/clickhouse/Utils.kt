/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse

import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path

val log = KotlinLogging.logger {}

object Utils {
    fun getConfigPath(relativePath: String): Path =
        Path.of(
            this::class.java.classLoader.getResource(relativePath)?.toURI()
                ?: throw IllegalArgumentException("Resource $relativePath could not be found")
        )
}
