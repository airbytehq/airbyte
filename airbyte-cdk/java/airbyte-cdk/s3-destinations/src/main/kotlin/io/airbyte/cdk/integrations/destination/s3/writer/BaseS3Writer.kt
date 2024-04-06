/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.writer

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateManager
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject
import io.airbyte.cdk.integrations.destination.s3.util.S3OutputPathHelper
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.io.IOException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*
import org.apache.commons.lang3.StringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * The base implementation takes care of the following:
 *
 * * Create shared instance variables.
 * * Create the bucket and prepare the bucket path.
 * * Log and close the write.
 */
abstract class BaseS3Writer
protected constructor(
    protected val config: S3DestinationConfig,
    protected val s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream
) : DestinationFileWriter {
    protected val stream: AirbyteStream = configuredStream.stream
    protected val syncMode: DestinationSyncMode = configuredStream.destinationSyncMode
    val outputPrefix: String? = S3OutputPathHelper.getOutputPrefix(config.bucketPath, stream)

    /**
     *
     * * 1. Create bucket if necessary.
     * * 2. Under OVERWRITE mode, delete all objects with the output prefix.
     */
    @Throws(IOException::class)
    override fun initialize() {
        try {
            val bucket = config.bucketName
            if (!s3Client.doesBucketExistV2(bucket)) {
                LOGGER.info("Bucket {} does not exist; creating...", bucket)
                s3Client.createBucket(bucket)
                LOGGER.info("Bucket {} has been created.", bucket)
            }

            if (syncMode == DestinationSyncMode.OVERWRITE) {
                LOGGER.info("Overwrite mode")
                val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
                val objects = s3Client.listObjects(bucket, outputPrefix).objectSummaries
                for (`object` in objects) {
                    keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
                }

                if (keysToDelete.size > 0) {
                    LOGGER.info(
                        "Purging non-empty output path for stream '{}' under OVERWRITE mode...",
                        stream.name
                    )
                    val result =
                        s3Client.deleteObjects(DeleteObjectsRequest(bucket).withKeys(keysToDelete))
                    LOGGER.info(
                        "Deleted {} file(s) for stream '{}'.",
                        result.deletedObjects.size,
                        stream.name
                    )
                }
            }
        } catch (e: Exception) {
            LOGGER.error("Failed to initialize: ", e)
            closeWhenFail()
            throw e
        }
    }

    /** Log and close the write. */
    @Throws(IOException::class)
    override fun close(hasFailed: Boolean) {
        if (hasFailed) {
            LOGGER.warn("Failure detected. Aborting upload of stream '{}'...", stream.name)
            closeWhenFail()
            LOGGER.warn("Upload of stream '{}' aborted.", stream.name)
        } else {
            LOGGER.info("Uploading remaining data for stream '{}'.", stream.name)
            closeWhenSucceed()
            LOGGER.info("Upload completed for stream '{}'.", stream.name)
        }
    }

    /** Operations that will run when the write succeeds. */
    @Throws(IOException::class)
    protected open fun closeWhenSucceed() {
        // Do nothing by default
    }

    /** Operations that will run when the write fails. */
    @Throws(IOException::class)
    protected open fun closeWhenFail() {
        // Do nothing by default
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(BaseS3Writer::class.java)

        private val s3FilenameTemplateManager = S3FilenameTemplateManager()
        private const val DEFAULT_SUFFIX = "_0"

        @JvmStatic
        @Throws(IOException::class)
        fun determineOutputFilename(parameterObject: S3FilenameTemplateParameterObject): String {
            return if (StringUtils.isNotBlank(parameterObject.fileNamePattern))
                getOutputFilename(parameterObject)
            else getDefaultOutputFilename(parameterObject)
        }

        /**
         * @param parameterObject
         * - an object which holds all necessary parameters required for default filename creation.
         * @return A string in the format
         * "{upload-date}_{upload-millis}_{suffix}.{format-extension}". For example,
         * "2021_12_09_1639077474000_customSuffix.csv"
         */
        private fun getDefaultOutputFilename(
            parameterObject: S3FilenameTemplateParameterObject
        ): String {
            val formatter: DateFormat =
                SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING)
            formatter.timeZone = TimeZone.getTimeZone("UTC")
            return String.format(
                "%s_%d%s.%s",
                formatter.format(parameterObject.timestamp),
                parameterObject.timestamp!!.time,
                parameterObject.customSuffix ?: DEFAULT_SUFFIX,
                parameterObject.s3Format!!.fileExtension
            )
        }

        @Throws(IOException::class)
        private fun getOutputFilename(parameterObject: S3FilenameTemplateParameterObject): String {
            return s3FilenameTemplateManager.applyPatternToFilename(parameterObject)
        }
    }
}
