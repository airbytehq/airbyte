/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.writer

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.HeadBucketRequest
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.cdk.integrations.destination.s3.util.S3OutputPathHelper.getOutputPrefix
import io.airbyte.cdk.integrations.destination.s3.writer.DestinationFileWriter
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.sql.Timestamp
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * The base implementation takes care of the following:
 *
 * * Create shared instance variables.
 * * Create the bucket and prepare the bucket path.
 */
abstract class BaseGcsWriter
protected constructor(
    protected val config: GcsDestinationConfig,
    protected val s3Client: AmazonS3,
    configuredStream: ConfiguredAirbyteStream
) : DestinationFileWriter {
    protected val stream: AirbyteStream = configuredStream.stream
    protected val syncMode: DestinationSyncMode? = configuredStream.destinationSyncMode
    protected val outputPrefix: String = getOutputPrefix(config.bucketPath, stream)

    /**
     *
     * * 1. Create bucket if necessary.
     * * 2. Under OVERWRITE mode, delete all objects with the output prefix.
     */
    @Throws(IOException::class)
    override fun initialize() {
        try {
            val bucket = config.bucketName
            if (!gcsBucketExist(s3Client, bucket)) {
                LOGGER.info { "Bucket $bucket does not exist; creating..." }
                s3Client.createBucket(bucket)
                LOGGER.info { "Bucket $bucket has been created." }
            }

            if (syncMode == DestinationSyncMode.OVERWRITE) {
                LOGGER.info { "Overwrite mode" }
                val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
                val objects = s3Client.listObjects(bucket, outputPrefix).objectSummaries
                for (`object` in objects) {
                    keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
                }

                if (keysToDelete.size > 0) {
                    LOGGER.info {
                        "Purging non-empty output path for stream '${stream.name}' under OVERWRITE mode..."
                    }
                    // Google Cloud Storage doesn't accept request to delete multiple objects
                    for (keyToDelete in keysToDelete) {
                        s3Client.deleteObject(bucket, keyToDelete.key)
                    }
                    LOGGER.info {
                        "Deleted ${keysToDelete.size} file(s) for stream '${stream.name}'."
                    }
                }
                LOGGER.info { "Overwrite is finished" }
            }
        } catch (e: Exception) {
            LOGGER.error(e) { "Failed to initialize: " }
            closeWhenFail()
            throw e
        }
    }

    /**
     * [AmazonS3.doesBucketExistV2] should be used to check the bucket existence. However, this
     * method does not work for GCS. So we use [AmazonS3.headBucket] instead, which will throw an
     * exception if the bucket does not exist, or there is no permission to access it.
     */
    fun gcsBucketExist(s3Client: AmazonS3, bucket: String?): Boolean {
        try {
            s3Client.headBucket(HeadBucketRequest(bucket))
            return true
        } catch (e: Exception) {
            return false
        }
    }

    @Throws(IOException::class)
    override fun close(hasFailed: Boolean) {
        if (hasFailed) {
            LOGGER.warn { "Failure detected. Aborting upload of stream '${stream.name}'..." }
            closeWhenFail()
            LOGGER.warn { "Upload of stream '${stream.name}' aborted." }
        } else {
            LOGGER.info { "Uploading remaining data for stream '${stream.name}'." }
            closeWhenSucceed()
            LOGGER.info { "Upload completed for stream '${stream.name}'." }
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

        // Filename: <upload-date>_<upload-millis>_0.<format-extension>
        fun getOutputFilename(timestamp: Timestamp, format: FileUploadFormat): String {
            val formatter: DateFormat =
                SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING)
            formatter.timeZone = TimeZone.getTimeZone("UTC")
            return String.format(
                "%s_%d_0.%s",
                formatter.format(timestamp),
                timestamp.time,
                format.fileExtension
            )
        }
    }
}
