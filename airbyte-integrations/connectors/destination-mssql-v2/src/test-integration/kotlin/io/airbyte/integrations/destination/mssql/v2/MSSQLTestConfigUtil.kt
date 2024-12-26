package io.airbyte.integrations.destination.mssql.v2

import java.nio.file.Path

object MSSQLTestConfigUtil {
    fun getConfigPath(relativePath: String): Path =
        Path.of(this::class.java.classLoader.getResource(relativePath)?.toURI() ?: throw IllegalArgumentException("Resource $relativePath could not be found"))
}
