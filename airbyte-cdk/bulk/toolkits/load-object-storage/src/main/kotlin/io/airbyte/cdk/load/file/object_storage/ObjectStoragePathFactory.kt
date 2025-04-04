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
    fun getLongestStreamConstantPrefix(stream: DestinationStream): String
    fun getFinalDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean = false
    ): String
    fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        extension: String? = null
    ): String
    fun getPathMatcher(stream: DestinationStream, suffixPattern: String? = null): PathMatcher

    val finalPrefix: String
}

data class PathMatcher(val regex: Regex, val variableToIndex: Map<String, Int>) {
    fun match(path: String): PathMatcherResult? {
        val match = regex.matchEntire(path) ?: return null

        val partNumber =
            try {
                variableToIndex["part_number"]?.let { match.groupValues[it].toLong() }
            } catch (e: Exception) {
                throw PathMatcherException(
                    "Could not parse part number from $path with pattern: ${regex.pattern} at index: ${variableToIndex["part_number"]}",
                    e,
                )
            }

        val suffix =
            try {
                variableToIndex["suffix"]?.let {
                    match.groupValues[it].let { g -> g.ifBlank { null } }
                }
            } catch (e: Exception) {
                throw PathMatcherException(
                    "Could not parse suffix from $path with pattern: ${regex.pattern} at index: ${variableToIndex["suffix"]}",
                    e,
                )
            }

        return PathMatcherResult(path, partNumber, suffix)
    }
}

data class PathMatcherResult(val path: String, val partNumber: Long?, val customSuffix: String?)

@Singleton
@Secondary
class ObjectStoragePathFactory(
    pathConfigProvider: ObjectStoragePathConfigurationProvider,
    formatConfigProvider: ObjectStorageFormatConfigurationProvider? = null,
    compressionConfigProvider: ObjectStorageCompressionConfigurationProvider<*>? = null,
    private val timeProvider: TimeProvider,
) : PathFactory {
    // Resolved configuration
    private val pathConfig = pathConfigProvider.objectStoragePathConfiguration

    // Resolved bucket path prefix
    override val finalPrefix: String =
        if (pathConfig.prefix.endsWith('/')) {
            pathConfig.prefix.take(pathConfig.prefix.length - 1)
        } else {
            pathConfig.prefix
        }

    // Resolved path and filename patterns
    private val pathPatternResolved = pathConfig.pathPattern ?: DEFAULT_PATH_FORMAT
    private val filePatternResolved = pathConfig.fileNamePattern ?: DEFAULT_FILE_FORMAT

    // Resolved file extensions
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

    /**
     * This is to maintain parity with legacy code. Whether the path pattern ends with "/" is
     * significant.
     *
     * * path: "{STREAM_NAME}/foo/" + "{part_number}{format_extension}" => "my_stream/foo/1.json"
     * * path: "{STREAM_NAME}/foo" + "{part_number}{format_extension}" => "my_stream/foo1.json"
     */
    private fun resolveRetainingTerminalSlash(prefix: String, suffix: String = ""): String {
        val asPath = Paths.get(prefix, suffix)
        return if ("$prefix$suffix".endsWith('/')) {
            "$asPath/"
        } else {
            asPath.toString()
        }
    }

    override fun getFinalDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean
    ): String {
        val path =
            getFormattedPath(
                stream,
                if (substituteStreamAndNamespaceOnly) PATH_VARIABLES_STREAM_CONSTANT
                else PATH_VARIABLES,
            )
        return resolveRetainingTerminalSlash(path)
    }

    override fun getLongestStreamConstantPrefix(
        stream: DestinationStream,
    ): String {
        return getFinalDirectory(stream, substituteStreamAndNamespaceOnly = true).takeWhile {
            it != '$'
        }
    }

    override fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        extension: String?
    ): String {
        val extensionResolved = extension ?: defaultExtension
        val path = getFinalDirectory(stream)
        val context =
            VariableContext(stream, extension = extensionResolved, partNumber = partNumber)
        val fileName = getFormattedFileName(context)
        // NOTE: The old code does not actually resolve the path + filename, even tho the
        // documentation says it does.
        return "$path$fileName"
    }

    private fun getFormattedPath(
        stream: DestinationStream,
        variables: List<PathVariable> = PATH_VARIABLES,
    ): String {
        val pattern = resolveRetainingTerminalSlash(finalPrefix, pathPatternResolved)
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
            it.variable to
                (
                // Only escape the pattern if
                //   A) it's not already provided
                //   B) the value from context is not blank
                // This is to ensure stream names/namespaces with special characters (foo+1) match
                // correctly,
                // but that blank patterns are ignored completely.
                it.pattern
                    ?: (it.provider(VariableContext(stream)).let { s ->
                        if (s.isNotBlank()) {
                            Regex.escape(s)
                        } else {
                            s
                        }
                    }))
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
        variableToIndex: MutableList<Pair<String, Int>>
    ): String {
        return Regex.escapeReplacement(input).replace(macroPattern.toRegex()) {
            val variable = it.groupValues[1]
            val pattern = variableToPattern[variable]
            if (pattern == null) {
                // This should happen if it wasn't a supported variable and is thus interpreted as
                // a string literal—e.g. ${FOOBAR} will be inserted as FOOBAR.
                variable
            } else if (pattern.isBlank()) {
                // This should only happen in the case of a blank namespace.
                // This is to avoid inserting `()` and then trying to match
                // `()/($streamName)` against `$streamName`.
                ""
            } else {
                variableToIndex.add(Pair(variable, variableToIndex.size + 1))
                "($pattern)"
            }
        }
    }

    override fun getPathMatcher(stream: DestinationStream, suffixPattern: String?): PathMatcher {
        val pathVariableToPattern = getPathVariableToPattern(stream)
        val variableIndexTuples = mutableListOf<Pair<String, Int>>()

        val pathPattern = resolveRetainingTerminalSlash(finalPrefix, pathPatternResolved)

        val replacedForPath =
            buildPattern(
                pathPattern,
                """\\\$\{(\w+)}""",
                pathVariableToPattern,
                variableIndexTuples
            )
        val replacedForFile =
            buildPattern(
                filePatternResolved,
                """\{([\w\:]+)}""",
                pathVariableToPattern,
                variableIndexTuples
            )
        // NOTE the old code does not actually resolve the path + filename,
        // even tho the documentation says it does.
        val replacedForPathWithEmptyVariablesRemoved =
            resolveRetainingTerminalSlash(replacedForPath)
        val combined = "$replacedForPathWithEmptyVariablesRemoved$replacedForFile"
        val withSuffix =
            if (suffixPattern != null) {
                variableIndexTuples.add(Pair("suffix", variableIndexTuples.size + 1))
                "$combined$suffixPattern"
            } else {
                combined
            }

        val variableToIndex = variableIndexTuples.toMap()
        return PathMatcher(Regex(withSuffix), variableToIndex)
    }
}
