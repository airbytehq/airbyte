/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Path
import java.nio.file.Paths
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*

@Singleton
@Secondary
class ObjectStoragePathFactory(
    pathConfigProvider: ObjectStoragePathConfigurationProvider,
    formatConfigProvider: ObjectStorageFormatConfigurationProvider? = null,
    compressionConfigProvider: ObjectStorageCompressionConfigurationProvider<*>? = null,
    timeProvider: TimeProvider? = null,
) {
    private val loadedAt = timeProvider?.let { Instant.ofEpochMilli(it.currentTimeMillis()) }
    private val pathConfig = pathConfigProvider.objectStoragePathConfiguration
    private val fileFormatExtension =
        formatConfigProvider?.objectStorageFormatConfiguration?.extension
    private val compressionExtension =
        compressionConfigProvider?.objectStorageCompressionConfiguration?.compressor?.extension
    private val defaultExtension =
        if (fileFormatExtension != null && compressionExtension != null) {
            "$fileFormatExtension.$compressionExtension"
        } else {
            fileFormatExtension ?: compressionExtension
        }

    inner class VariableContext(
        val stream: DestinationStream,
        val time: Instant? = loadedAt,
        val extension: String? = null,
        val partNumber: Long? = null
    )

    interface Variable {
        val provider: (VariableContext) -> String
        fun toMacro(): String
        fun maybeApply(source: String, context: VariableContext): String {
            val macro = toMacro()
            if (source.contains(macro)) {
                return source.replace(macro, provider(context))
            }
            return source
        }
    }

    data class PathVariable(
        val variable: String,
        override val provider: (VariableContext) -> String
    ) : Variable {
        override fun toMacro(): String = "\${$variable}"
    }

    data class FileVariable(
        val variable: String,
        override val provider: (VariableContext) -> String
    ) : Variable {
        override fun toMacro(): String = "{$variable}"
    }

    companion object {
        private val DATE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern("yyyy-MM-dd").withZone(ZoneId.systemDefault())
        private val TIMESTAMP_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSX").withZone(ZoneId.of("UTC"))

        const val DEFAULT_STAGING_PREFIX_SUFFIX = "__airbyte_tmp"
        const val DEFAULT_PATH_FORMAT =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"
        const val DEFAULT_FILE_FORMAT = "{part_number}{format_extension}"
        val PATH_VARIABLES =
        // TODO: Vet that these match the past format exactly (eg day = 5 versus 05, etc)
        listOf(
                PathVariable("NAMESPACE") { it.stream.descriptor.namespace ?: "" },
                PathVariable("STREAM_NAME") { it.stream.descriptor.name },
                PathVariable("YEAR") {
                    it.time?.let { t ->
                        ZonedDateTime.ofInstant(t, ZoneId.of("UTC")).year.toString()
                    }
                        ?: throw IllegalArgumentException("time is required when {YEAR} is present")
                },
                PathVariable("MONTH") {
                    it.time?.let { t ->
                        ZonedDateTime.ofInstant(t, ZoneId.of("UTC")).monthValue.toString()
                    }
                        ?: throw IllegalArgumentException(
                            "time is required when {MONTH} is present"
                        )
                },
                PathVariable("DAY") {
                    it.time?.let { t ->
                        ZonedDateTime.ofInstant(t, ZoneId.of("UTC")).dayOfMonth.toString()
                    }
                        ?: throw IllegalArgumentException("time is required when {DAY} is present")
                },
                PathVariable("HOUR") {
                    it.time?.toEpochMilli()?.let { t -> t / 1000 / 60 / 60 }?.toString()
                        ?: throw IllegalArgumentException("time is required when {HOUR} is present")
                },
                PathVariable("MINUTE") {
                    (it.time?.toEpochMilli()?.let { t -> t / 1000 / 60 }?.toString()
                        ?: throw IllegalArgumentException(
                            "time is required when {MINUTE} is present"
                        ))
                },
                PathVariable("SECOND") {
                    (it.time?.toEpochMilli()?.div(1000)?.toString()
                        ?: throw IllegalArgumentException(
                            "time is required when {SECOND} is present"
                        ))
                },
                PathVariable("MILLISECOND") {
                    it.time?.toEpochMilli()?.toString()
                        ?: throw IllegalArgumentException(
                            "time is required when {MILLISECOND} is present"
                        )
                },
                PathVariable("EPOCH") {
                    it.time?.toEpochMilli()?.toString()
                        ?: throw IllegalArgumentException(
                            "time is required when {EPOCH} is present"
                        )
                },
                PathVariable("UUID") { UUID.randomUUID().toString() }
            )
        val FILENAME_VARIABLES =
            listOf(
                FileVariable("date") { DATE_FORMATTER.format(it.time) },
                FileVariable("timestamp") { TIMESTAMP_FORMATTER.format(it.time) },
                FileVariable("part_number") {
                    it.partNumber?.toString()
                        ?: throw IllegalArgumentException(
                            "part_number is required when {part_number} is present"
                        )
                },
                FileVariable("sync_id") { it.stream.syncId.toString() },
                FileVariable("format_extension") { it.extension?.let { ext -> ".$ext" } ?: "" }
            )

        fun <T> from(config: T, timeProvider: TimeProvider? = null): ObjectStoragePathFactory where
        T : ObjectStoragePathConfigurationProvider,
        T : ObjectStorageFormatConfigurationProvider,
        T : ObjectStorageCompressionConfigurationProvider<*> {
            return ObjectStoragePathFactory(config, config, config, timeProvider)
        }
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

    fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        isStaging: Boolean = false,
        extension: String? = defaultExtension
    ): Path {
        val path =
            if (isStaging) {
                getStagingDirectory(stream)
            } else {
                getFinalDirectory(stream)
            }
        val context = VariableContext(stream, extension = extension, partNumber = partNumber)
        val fileName = getFormattedFileName(context)
        return path.resolve(fileName)
    }

    private fun getFormattedPath(stream: DestinationStream): String {
        val pattern = pathConfig.pathSuffixPattern ?: DEFAULT_PATH_FORMAT
        val context = VariableContext(stream)
        return PATH_VARIABLES.fold(pattern) { acc, variable -> variable.maybeApply(acc, context) }
    }

    private fun getFormattedFileName(context: VariableContext): String {
        val pattern = pathConfig.fileNamePattern ?: DEFAULT_FILE_FORMAT
        return FILENAME_VARIABLES.fold(pattern) { acc, variable ->
            variable.maybeApply(acc, context)
        }
    }
}
