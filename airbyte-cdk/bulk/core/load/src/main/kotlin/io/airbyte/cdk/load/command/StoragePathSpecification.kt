/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import java.nio.file.Path
import java.nio.file.Paths
import java.util.*
import org.joda.time.DateTime

interface S3PathSpecification {
    @get:JsonSchemaTitle("S3 Path Format")
    @get:JsonPropertyDescription(
        "Format string on how data will be organized inside the bucket directory. Read more <a href=\"https://docs.airbyte.com/integrations/destinations/s3#:~:text=The%20full%20path%20of%20the%20output%20data%20with%20the%20default%20S3%20path%20format\">here</a>"
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"]}"
    )
    @get:JsonProperty("s3_path_format")
    val s3PathFormat: String?

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern to match file names in the bucket directory. Read more <a href=\"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ListingKeysUsingAPIs.html\">here</a>"
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"]}"
    )
    @get:JsonProperty("file_name_pattern")
    val fileNamePattern: String?

    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "Directory under the S3 bucket where data will be written. Read more <a href=\"https://docs.airbyte.com/integrations/destinations/s3#:~:text=to%20format%20the-,bucket%20path,-%3A\">here</a>"
    )
    @get:JsonProperty("s3_bucket_path")
    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"]}""")
    val s3BucketPath: String

    fun toStoragePathConfiguration(): StoragePathConfiguration =
        StoragePathConfiguration(
            prefix = s3BucketPath,
            stagingPrefix = null,
            pathFormat = s3PathFormat,
            fileNamePattern = fileNamePattern
        )
}

data class StoragePathConfiguration(
    val prefix: String,
    val stagingPrefix: String?,
    val pathFormat: String?,
    val fileNamePattern: String?
)

interface StoragePathConfigurationProvider {
    val pathConfiguration: StoragePathConfiguration
}

fun <T> T.toPathFactory(loadedAt: DateTime): StoragePathFactory where
T : StoragePathConfigurationProvider,
T : OutputFormatConfigurationProvider =
    StoragePathFactory(loadedAt, pathConfiguration, outputFormat.extension)

class StoragePathFactory(
    private val loadedAt: DateTime,
    private val pathConfig: StoragePathConfiguration,
    private val fileExtension: String
) {
    inner class VariableContext(
        val stream: DestinationStream,
        val time: DateTime = loadedAt,
        val extension: String? = fileExtension
    )

    data class PathVariable(val variable: String, val provider: (VariableContext) -> String) {
        fun toMacro(): String = "\${$variable}"
    }

    data class FileVariable(val variable: String, val provider: (VariableContext) -> String) {
        fun toMacro(): String = "{$variable}"
    }

    companion object {
        const val DEFAULT_STAGING_PREFIX = "__airbyte_tmp"
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
        val FILENAME_VARIABLES =
            listOf(
                FileVariable("date") { it.time.toString("yyyy-MM-dd") },
                FileVariable("timestamp") { it.time.toString("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'") },
                FileVariable("part_number") { it.stream.generationId.toString() },
                FileVariable("sync_id") { it.stream.syncId.toString() },
                FileVariable("format_extension") { it.extension?.let { ext -> ".$ext" } ?: "" }
            )
    }

    fun getDirectory(
        stream: DestinationStream,
        isStaging: Boolean,
    ): Path {
        val format = pathConfig.pathFormat ?: DEFAULT_PATH_FORMAT
        val formattedPath =
            PATH_VARIABLES.fold(format) { acc, pathVariable ->
                acc.replace(
                    pathVariable.toMacro(),
                    pathVariable.provider(VariableContext(stream, loadedAt))
                )
            }
        val prefix =
            if (isStaging) {
                val stagingPrefix = pathConfig.stagingPrefix ?: DEFAULT_STAGING_PREFIX
                Paths.get(pathConfig.prefix, stagingPrefix).toString()
            } else {
                pathConfig.prefix
            }
        return Paths.get(prefix, formattedPath)
    }

    fun getFinalFilePath(stream: DestinationStream, partNumber: Long): Path {
        val directory = getDirectory(stream, false)
        val fileName = "${partNumber}.${fileExtension}"
        // TODO: Add the formatted filename
        return Paths.get(directory.toString(), fileName)
    }
}
