/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.file.DefaultTimeProvider
import io.airbyte.cdk.load.file.TimeProvider
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Paths
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*

interface PathFactory {
    fun getLongestStreamConstantPrefix(stream: DestinationStream, isStaging: Boolean): String
    fun getStagingDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean = false
    ): String
    fun getFinalDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean = false
    ): String
    fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        isStaging: Boolean = false,
        extension: String? = null
    ): String
    fun getPathMatcher(stream: DestinationStream): PathMatcher

    val supportsStaging: Boolean
    val prefix: String
}

data class PathMatcher(val regex: Regex, val variableToIndex: Map<String, Int>) {
    fun match(path: String): PathMatcherResult? {
        val match = regex.matchEntire(path) ?: return null
        return PathMatcherResult(
            path,
            variableToIndex["part_number"]?.let { match.groupValues[it].toLong() }
        )
    }
}

data class PathMatcherResult(val path: String, val partNumber: Long?)

@Singleton
@Secondary
class ObjectStoragePathFactory(
    pathConfigProvider: ObjectStoragePathConfigurationProvider,
    formatConfigProvider: ObjectStorageFormatConfigurationProvider? = null,
    compressionConfigProvider: ObjectStorageCompressionConfigurationProvider<*>? = null,
    private val timeProvider: TimeProvider,
) : PathFactory {
    private val pathConfig = pathConfigProvider.objectStoragePathConfiguration
    private val stagingPrefixResolved =
        pathConfig.stagingPrefix
            ?: Paths.get(pathConfig.prefix, DEFAULT_STAGING_PREFIX_SUFFIX).toString()
    private val pathPatternResolved = pathConfig.pathSuffixPattern ?: DEFAULT_PATH_FORMAT
    private val filePatternResolved = pathConfig.fileNamePattern ?: DEFAULT_FILE_FORMAT
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

    private val stagingPrefix: String
        get() =
            if (!pathConfig.usesStagingDirectory) {
                throw UnsupportedOperationException(
                    "Staging is not supported by this configuration"
                )
            } else {
                stagingPrefixResolved
            }

    override val supportsStaging: Boolean = pathConfig.usesStagingDirectory
    override val prefix: String =
        if (pathConfig.prefix.endsWith('/')) {
            pathConfig.prefix.take(pathConfig.prefix.length - 1)
        } else {
            pathConfig.prefix
        }

    /**
     * Variable substitution is complex.
     *
     * 1. There are two types: path variables and file name variables.
     * 2. Path variables use the ${NAME} syntax, while file name variables use the {name} syntax. (I
     * have no idea why this is.)
     * 3. A variable is defined by a [Variable.pattern] and a [Variable.provider]
     * 4. [Variable.provider] is a function that takes a [VariableContext] and returns a string.
     * It's used for substitution to get the actual path.
     * 5. [Variable.pattern] is a regex pattern that can match any results of [Variable.provider].
     * 6. If [Variable.pattern] is null, [Variable.provider] is used to get the value. (Ie, we won't
     * match against a pattern, but always against the realized value. In practice this is for
     * stream name and namespace, because matching always performed at the stream level.)
     * 7. Matching should be considered deprecated. It is only required for configurations that do
     * not enable staging, which populate destination state by collecting metadata from object
     * headers. It is extremely brittle and can break against malformed paths or paths that do not
     * include enough variables to avoid clashes. If you run into a client issue which requires a
     * path change anyway (a breaking change for some workflows), consider advising them to enable
     * staging.
     */
    inner class VariableContext(
        val stream: DestinationStream,
        val syncTime: Instant = Instant.ofEpochMilli(timeProvider.syncTimeMillis()),
        val currentTimeProvider: TimeProvider = timeProvider,
        val extension: String? = null,
        val partNumber: Long? = null
    )

    interface Variable {
        val pattern: String?
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
        override val pattern: String? = null,
        override val provider: (VariableContext) -> String,
    ) : Variable {
        override fun toMacro(): String = "\${$variable}"
    }

    data class FileVariable(
        val variable: String,
        override val pattern: String? = null,
        override val provider: (VariableContext) -> String,
    ) : Variable {
        override fun toMacro(): String = "{$variable}"
    }

    companion object {
        private val DATE_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern("yyyy_MM_dd").withZone(ZoneId.systemDefault())

        const val DEFAULT_STAGING_PREFIX_SUFFIX = "__airbyte_tmp"
        const val DEFAULT_PATH_FORMAT =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"
        const val DEFAULT_FILE_FORMAT = "{part_number}{format_extension}"
        val PATH_VARIABLES =
            listOf(
                PathVariable("NAMESPACE") {
                    Transformations.toS3SafeCharacters(it.stream.descriptor.namespace ?: "")
                },
                PathVariable("STREAM_NAME") {
                    Transformations.toS3SafeCharacters(it.stream.descriptor.name)
                },
                PathVariable("YEAR", """\d{4}""") {
                    ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).year.toString()
                },
                PathVariable("MONTH", """\d{2}""") {
                    String.format(
                        "%02d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).monthValue
                    )
                },
                PathVariable("DAY", """\d{2}""") {
                    String.format(
                        "%02d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).dayOfMonth
                    )
                },
                PathVariable("HOUR", """\d{2}""") {
                    String.format(
                        "%02d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).hour
                    )
                },
                PathVariable("MINUTE", """\d{2}""") {
                    String.format(
                        "%02d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).minute
                    )
                },
                PathVariable("SECOND", """\d{2}""") {
                    String.format(
                        "%02d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC")).second
                    )
                },
                PathVariable("MILLISECOND", """\d{4}""") {
                    // Unclear why this is %04d, but that's what it was in the old code
                    String.format(
                        "%04d",
                        ZonedDateTime.ofInstant(it.syncTime, ZoneId.of("UTC"))
                            .toLocalTime()
                            .toNanoOfDay() / 1_000_000 % 1_000
                    )
                },
                PathVariable("EPOCH", """\d+""") { it.syncTime.toEpochMilli().toString() },
                PathVariable("UUID", """[a-fA-F0-9\\-]{36}""") { UUID.randomUUID().toString() }
            )
        val PATH_VARIABLES_STREAM_CONSTANT =
            PATH_VARIABLES.filter { it.variable == "NAMESPACE" || it.variable == "STREAM_NAME" }
        val FILENAME_VARIABLES =
            listOf(
                FileVariable("date", """\d{4}_\d{2}_\d{2}""") {
                    DATE_FORMATTER.format(it.syncTime)
                },
                FileVariable("date:yyyy_MM", """\d{4}_\d{2}""") {
                    DATE_FORMATTER.format(it.syncTime).substring(0, 7)
                },
                FileVariable("timestamp", """\d+""") {
                    // NOTE: We use a constant time for the path but wall time for the files
                    it.currentTimeProvider.currentTimeMillis().toString()
                },
                FileVariable("part_number", """\d+""") {
                    it.partNumber?.toString()
                        ?: throw IllegalArgumentException(
                            "part_number is required when {part_number} is present"
                        )
                },
                FileVariable("sync_id", """\d+""") { it.stream.syncId.toString() },
                FileVariable("format_extension") { it.extension?.let { ext -> ".$ext" } ?: "" }
            )

        fun <T> from(
            config: T,
            timeProvider: TimeProvider = DefaultTimeProvider()
        ): ObjectStoragePathFactory where
        T : ObjectStoragePathConfigurationProvider,
        T : ObjectStorageFormatConfigurationProvider,
        T : ObjectStorageCompressionConfigurationProvider<*> {
            return ObjectStoragePathFactory(config, config, config, timeProvider)
        }
    }

    private fun resolveRetainingTerminalSlash(prefix: String, path: String): String {
        val asPath = Paths.get(prefix, path)
        return if (path.endsWith('/')) {
            asPath.toString() + "/"
        } else {
            asPath.toString()
        }
    }

    override fun getStagingDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean
    ): String {
        val path =
            getFormattedPath(
                stream,
                if (substituteStreamAndNamespaceOnly) PATH_VARIABLES_STREAM_CONSTANT
                else PATH_VARIABLES
            )
        return resolveRetainingTerminalSlash(stagingPrefix, path)
    }

    override fun getFinalDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean
    ): String {
        val path =
            getFormattedPath(
                stream,
                if (substituteStreamAndNamespaceOnly) PATH_VARIABLES_STREAM_CONSTANT
                else PATH_VARIABLES
            )
        return resolveRetainingTerminalSlash(prefix, path)
    }

    override fun getLongestStreamConstantPrefix(
        stream: DestinationStream,
        isStaging: Boolean
    ): String {
        return if (isStaging) {
                getStagingDirectory(stream, substituteStreamAndNamespaceOnly = true)
            } else {
                getFinalDirectory(stream, substituteStreamAndNamespaceOnly = true)
            }
            .takeWhile { it != '$' }
    }

    override fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        isStaging: Boolean,
        extension: String?
    ): String {
        val extensionResolved = extension ?: defaultExtension
        val path =
            if (isStaging) {
                    getStagingDirectory(stream)
                } else {
                    getFinalDirectory(stream)
                }
                .toString()
        val context =
            VariableContext(stream, extension = extensionResolved, partNumber = partNumber)
        val fileName = getFormattedFileName(context)
        // NOTE: The old code does not actually resolve the path + filename, even tho the
        // documentation says it does.
        return "$path$fileName"
    }

    private fun getFormattedPath(
        stream: DestinationStream,
        variables: List<PathVariable> = PATH_VARIABLES
    ): String {
        val pattern = pathPatternResolved
        val context = VariableContext(stream)
        return variables.fold(pattern) { acc, variable -> variable.maybeApply(acc, context) }
    }

    private fun getFormattedFileName(context: VariableContext): String {
        val pattern = filePatternResolved
        return FILENAME_VARIABLES.fold(pattern) { acc, variable ->
            variable.maybeApply(acc, context)
        }
    }

    private fun getPathVariableToPattern(stream: DestinationStream): Map<String, String> {
        return PATH_VARIABLES.associate {
            it.variable to (it.pattern ?: it.provider(VariableContext(stream)))
        } +
            FILENAME_VARIABLES.associate {
                it.variable to
                    (it.pattern
                        ?: it.provider(VariableContext(stream, extension = defaultExtension)))
            }
    }

    private fun buildPattern(
        input: String,
        macroPattern: String,
        variableToPattern: Map<String, String>,
        variableToIndex: MutableMap<String, Int>
    ): String {
        return Regex.escapeReplacement(input).replace(macroPattern.toRegex()) {
            val variable = it.groupValues[1]
            val pattern = variableToPattern[variable]
            if (pattern == null) {
                variable
            } else if (pattern.isBlank()) {
                // This should only happen in the case of a blank namespace.
                // This is to avoid inserting `()` and then trying to match
                // `()/($streamName)` against `$streamName`.
                ""
            } else {
                variableToIndex[variable] = variableToIndex.size + 1
                "($pattern)"
            }
        }
    }

    override fun getPathMatcher(stream: DestinationStream): PathMatcher {
        val pathVariableToPattern = getPathVariableToPattern(stream)
        val variableToIndex = mutableMapOf<String, Int>()

        val replacedForPath =
            buildPattern(
                pathPatternResolved,
                """\\\$\{(\w+)}""",
                pathVariableToPattern,
                variableToIndex
            )
        val replacedForFile =
            buildPattern(
                filePatternResolved,
                """\{([\w\:]+)}""",
                pathVariableToPattern,
                variableToIndex
            )
        // NOTE the old code does not actually resolve the path + filename,
        // even tho the documentation says it does.
        val combined =
            if (replacedForPath.startsWith('/')) {
                "${prefix}$replacedForPath$replacedForFile"
            } else {
                "$prefix/$replacedForPath$replacedForFile"
            }
        return PathMatcher(Regex(combined), variableToIndex)
    }
}
