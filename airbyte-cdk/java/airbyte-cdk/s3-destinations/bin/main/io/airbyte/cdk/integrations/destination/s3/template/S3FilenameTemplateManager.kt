/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.template

import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import java.io.IOException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.time.Instant
import java.util.Optional
import java.util.TimeZone
import java.util.regex.Pattern
import org.apache.commons.lang3.StringUtils
import org.apache.commons.text.StringSubstitutor
import org.apache.commons.text.lookup.StringLookupFactory

/**
 * This class is responsible for building the filename template based on user input, see
 * file_name_pattern in the specification of connector currently supported only S3 staging.
 */
class S3FilenameTemplateManager {
    private val stringSubstitutor = StringSubstitutor()

    @Throws(IOException::class)
    fun applyPatternToFilename(parameterObject: S3FilenameTemplateParameterObject): String {
        // sanitize fileFormat
        val sanitizedFileFormat =
            parameterObject.fileNamePattern?.trim { it <= ' ' }?.replace(" ".toRegex(), "_")

        stringSubstitutor.setVariableResolver(
            StringLookupFactory.INSTANCE.mapStringLookup(
                fillTheMapWithDefaultPlaceHolders(
                    sanitizedFileFormat,
                    parameterObject,
                ),
            ),
        )
        stringSubstitutor.setVariablePrefix("{")
        stringSubstitutor.setVariableSuffix("}")
        return Optional.ofNullable(parameterObject.objectPath).orElse(StringUtils.EMPTY) +
            stringSubstitutor.replace(sanitizedFileFormat)
    }

    private fun fillTheMapWithDefaultPlaceHolders(
        stringToReplaceWithPlaceholder: String?,
        parameterObject: S3FilenameTemplateParameterObject
    ): Map<String, String> {
        val currentTimeMillis = Instant.now().toEpochMilli()

        val valuesMap =
            processExtendedPlaceholder(currentTimeMillis, stringToReplaceWithPlaceholder)

        val defaultDateFormat: DateFormat =
            SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING)
        defaultDateFormat.timeZone = TimeZone.getTimeZone(UTC)

        // here we set default values for supported placeholders.
        valuesMap["date"] =
            Optional.ofNullable(defaultDateFormat.format(currentTimeMillis))
                .orElse(
                    StringUtils.EMPTY,
                )
        valuesMap["timestamp"] =
            Optional.ofNullable(currentTimeMillis.toString()).orElse(StringUtils.EMPTY)
        valuesMap["sync_id"] =
            Optional.ofNullable(System.getenv("WORKER_JOB_ID")).orElse(StringUtils.EMPTY)
        valuesMap["format_extension"] =
            Optional.ofNullable(parameterObject.fileExtension).orElse(StringUtils.EMPTY)
        valuesMap["part_number"] =
            Optional.ofNullable(parameterObject.partId).orElse(StringUtils.EMPTY)

        return valuesMap
    }

    /**
     * By extended placeholders we assume next types: {date:yyyy_MM}, {timestamp:millis},
     * {timestamp:micro}, etc Limited combinations are supported by the method see the method body.
     *
     * @param stringToReplaceWithPlaceholder
     * - string where the method will search for extended placeholders
     * @return map with prepared placeholders.
     */
    private fun processExtendedPlaceholder(
        currentTimeMillis: Long,
        stringToReplaceWithPlaceholder: String?
    ): MutableMap<String, String> {
        val valuesMap: MutableMap<String, String> = HashMap()

        val pattern = Pattern.compile("\\{(date:.+?|timestamp:.+?)}")
        val matcher = stringToReplaceWithPlaceholder?.let { pattern.matcher(it) }

        while (matcher?.find() == true) {
            val splitByColon =
                matcher.group(1).split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
            when (splitByColon[0].lowercase()) {
                "date" -> {
                    val dateFormat: DateFormat = SimpleDateFormat(splitByColon[1])
                    dateFormat.timeZone = TimeZone.getTimeZone("UTC")
                    valuesMap[matcher.group(1)] = dateFormat.format(currentTimeMillis)
                }
                "timestamp" -> {
                    when (splitByColon[1]) {
                        "millis" -> {
                            valuesMap[matcher.group(1)] = currentTimeMillis.toString()
                        }
                        "micro" -> {
                            valuesMap[matcher.group(1)] =
                                convertToMicrosecondsRepresentation(currentTimeMillis).toString()
                        }
                    }
                }
            }
        }
        return valuesMap
    }

    private fun convertToMicrosecondsRepresentation(milliSeconds: Long): Long {
        // The time representation in microseconds is equal to the milliseconds multiplied by 1,000.
        return milliSeconds * 1000
    }

    companion object {
        private const val UTC = "UTC"
    }
}
