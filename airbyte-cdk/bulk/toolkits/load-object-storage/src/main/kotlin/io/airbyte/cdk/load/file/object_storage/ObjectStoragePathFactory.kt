/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Path
import java.nio.file.Paths
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import java.util.*

@Singleton
@Secondary
class ObjectStoragePathFactory(
    pathConfigProvider: ObjectStoragePathConfigurationProvider,
    timeProvider: TimeProvider
) {
    private val loadedAt = Instant.ofEpochMilli(timeProvider.currentTimeMillis())
    private val pathConfig = pathConfigProvider.objectStoragePathConfiguration

    inner class VariableContext(
        val stream: DestinationStream,
        val time: Instant = loadedAt,
    )

    data class PathVariable(val variable: String, val provider: (VariableContext) -> String) {
        fun toMacro(): String = "\${$variable}"
    }

    companion object {
        const val DEFAULT_STAGING_PREFIX_SUFFIX = "__airbyte_tmp"
        const val DEFAULT_PATH_FORMAT =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"
        val PATH_VARIABLES =
        // TODO: Vet that these match the past format exactly (eg day = 5 versus 05, etc)
        listOf(
                PathVariable("NAMESPACE") { it.stream.descriptor.namespace ?: "" },
                PathVariable("STREAM_NAME") { it.stream.descriptor.name },
                PathVariable("YEAR") {
                    ZonedDateTime.ofInstant(it.time, ZoneId.of("UTC")).year.toString()
                },
                PathVariable("MONTH") {
                    ZonedDateTime.ofInstant(it.time, ZoneId.of("UTC")).monthValue.toString()
                },
                PathVariable("DAY") {
                    ZonedDateTime.ofInstant(it.time, ZoneId.of("UTC")).dayOfMonth.toString()
                },
                PathVariable("HOUR") { (it.time.toEpochMilli() / 1000 / 60 / 60).toString() },
                PathVariable("MINUTE") { (it.time.toEpochMilli() / 1000 / 60).toString() },
                PathVariable("SECOND") { (it.time.toEpochMilli() / 1000).toString() },
                PathVariable("MILLISECOND") { it.time.toEpochMilli().toString() },
                PathVariable("EPOCH") { it.time.toEpochMilli().toString() },
                PathVariable("UUID") { UUID.randomUUID().toString() }
            )
    }

    fun getStagingDirectory(stream: DestinationStream): Path {
        val prefix =
            pathConfig.stagingPrefix
                ?: Paths.get(pathConfig.prefix, DEFAULT_STAGING_PREFIX_SUFFIX).toString()
        val path = getFormattedPath(stream)
        return Paths.get(prefix, path)
    }

    fun getFinalDirectory(stream: DestinationStream): Path {
        val path = getFormattedPath(stream)
        return Paths.get(pathConfig.prefix, path)
    }

    private fun getFormattedPath(stream: DestinationStream): String {
        val pattern = pathConfig.pathSuffixPattern ?: DEFAULT_PATH_FORMAT
        return PATH_VARIABLES.fold(pattern) { acc, variable ->
            acc.replace(variable.toMacro(), variable.provider(VariableContext(stream)))
        }
    }
}
