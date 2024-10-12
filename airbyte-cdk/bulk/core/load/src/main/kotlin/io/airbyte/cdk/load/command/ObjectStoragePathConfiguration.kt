/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import java.nio.file.Path
import java.nio.file.Paths
import java.util.*
import org.joda.time.DateTime

data class ObjectStoragePathConfiguration(
    val prefix: String,
    val stagingPrefix: String?,
    val pathSuffixPattern: String?,
    val fileNamePattern: String?
)

interface ObjectStoragePathConfigurationProvider {
    val objectStoragePathConfiguration: ObjectStoragePathConfiguration

    fun createPathFactory(loadedAtMs: Long): ObjectStoragePathFactory {
        return ObjectStoragePathFactory(objectStoragePathConfiguration, DateTime(loadedAtMs))
    }
}

class ObjectStoragePathFactory(
    private val pathConfig: ObjectStoragePathConfiguration,
    private val loadedAt: DateTime
) {
    inner class VariableContext(
        val stream: DestinationStream,
        val time: DateTime = loadedAt,
    )

    data class PathVariable(val variable: String, val provider: (VariableContext) -> String) {
        fun toMacro(): String = "\${$variable}"
    }

    companion object {
        const val DEFAULT_STAGING_PREFIX_SUFFIX = "__airbyte_tmp"
        const val DEFAULT_PATH_FORMAT =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"
        val PATH_VARIABLES =
            listOf(
                PathVariable("NAMESPACE") { it.stream.descriptor.namespace ?: "" },
                PathVariable("STREAM_NAME") { it.stream.descriptor.name },
                PathVariable("YEAR") { it.time.year().get().toString() },
                PathVariable("MONTH") { it.time.monthOfYear().get().toString() },
                PathVariable("DAY") { it.time.dayOfMonth().get().toString() },
                PathVariable("HOUR") { it.time.hourOfDay().get().toString() },
                PathVariable("MINUTE") { it.time.minuteOfHour().get().toString() },
                PathVariable("SECOND") { it.time.secondOfMinute().get().toString() },
                PathVariable("MILLISECOND") { it.time.millisOfSecond().get().toString() },
                PathVariable("EPOCH") { it.time.millis.toString() },
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
