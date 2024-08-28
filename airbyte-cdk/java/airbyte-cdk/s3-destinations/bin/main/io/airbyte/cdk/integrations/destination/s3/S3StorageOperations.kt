/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.AmazonS3Exception
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.ListObjectsRequest
import com.amazonaws.services.s3.model.ObjectListing
import com.amazonaws.services.s3.model.S3ObjectSummary
import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateManager
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.commons.exceptions.ConfigErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.OutputStream
import java.util.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.regex.Pattern
import org.apache.commons.io.FilenameUtils
import org.joda.time.DateTime

private val logger = KotlinLogging.logger {}

open class S3StorageOperations(
    private val nameTransformer: NamingConventionTransformer,
    var s3Client: AmazonS3,
    private val s3Config: S3DestinationConfig
) : BlobStorageOperations() {
    private val s3FilenameTemplateManager: S3FilenameTemplateManager = S3FilenameTemplateManager()

    private val partCounts: ConcurrentMap<String, AtomicInteger> = ConcurrentHashMap()

    override fun getBucketObjectPath(
        namespace: String?,
        streamName: String,
        writeDatetime: DateTime,
        customFormat: String
    ): String {
        val namespaceStr: String =
            nameTransformer.getNamespace(if (!namespace.isNullOrBlank()) namespace else "")
        val streamNameStr: String = nameTransformer.getIdentifier(streamName)
        return nameTransformer.applyDefaultCase(
            customFormat
                .replace(Pattern.quote(FORMAT_VARIABLE_NAMESPACE).toRegex(), namespaceStr)
                .replace(Pattern.quote(FORMAT_VARIABLE_STREAM_NAME).toRegex(), streamNameStr)
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_YEAR).toRegex(),
                    String.format("%s", writeDatetime.year().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_MONTH).toRegex(),
                    String.format("%02d", writeDatetime.monthOfYear().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_DAY).toRegex(),
                    String.format("%02d", writeDatetime.dayOfMonth().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_HOUR).toRegex(),
                    String.format("%02d", writeDatetime.hourOfDay().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_MINUTE).toRegex(),
                    String.format("%02d", writeDatetime.minuteOfHour().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_SECOND).toRegex(),
                    String.format("%02d", writeDatetime.secondOfMinute().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_MILLISECOND).toRegex(),
                    String.format("%04d", writeDatetime.millisOfSecond().get()),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_EPOCH).toRegex(),
                    String.format("%d", writeDatetime.millis),
                )
                .replace(
                    Pattern.quote(FORMAT_VARIABLE_UUID).toRegex(),
                    String.format("%s", UUID.randomUUID()),
                )
                .replace("/+".toRegex(), "/"),
        )
    }

    /** Create a directory object at the specified location. Creates the bucket if necessary. */
    override fun createBucketIfNotExists() {
        val bucket: String? = s3Config.bucketName
        if (!doesBucketExist(bucket)) {
            logger.info { "Bucket $bucket does not exist; creating..." }
            s3Client.createBucket(bucket)
            logger.info { "Bucket $bucket has been created." }
        }
    }

    protected open fun doesBucketExist(bucket: String?): Boolean {
        return s3Client.doesBucketExistV2(bucket)
    }

    override fun uploadRecordsToBucket(
        recordsData: SerializableBuffer,
        namespace: String?,
        objectPath: String
    ): String {
        val exceptionsThrown: MutableList<Exception> = ArrayList()
        while (exceptionsThrown.size < UPLOAD_RETRY_LIMIT) {
            if (exceptionsThrown.isNotEmpty()) {
                logger.info {
                    "Retrying to upload records into storage $objectPath (${exceptionsThrown.size}/$UPLOAD_RETRY_LIMIT)"
                }
                // Force a reconnection before retrying in case error was due to network issues...
                s3Client = s3Config.resetS3Client()
            }

            try {
                val fileName: String = loadDataIntoBucket(objectPath, recordsData)
                logger.info {
                    "Successfully loaded records to stage $objectPath with ${exceptionsThrown.size} re-attempt(s)"
                }
                return fileName
            } catch (e: Exception) {
                logger.error(e) { "Failed to upload records into storage $objectPath" }
                exceptionsThrown.add(e)
            }
        }
        // Verifying that ALL exceptions are authentication related before assuming this is a
        // configuration
        // issue reduces risk of misidentifying errors or reporting a transient error.
        val areAllExceptionsAuthExceptions: Boolean =
            exceptionsThrown
                .filterIsInstance<AmazonS3Exception>()
                .map { s3e: Exception -> (s3e as AmazonS3Exception).statusCode }
                .count { o: Int ->
                    ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(
                        o,
                    )
                } == exceptionsThrown.size
        if (areAllExceptionsAuthExceptions) {
            throw ConfigErrorException(exceptionsThrown[0].message!!, exceptionsThrown[0])
        } else {
            throw RuntimeException(
                "Exceptions thrown while uploading records into storage: ${exceptionsThrown.joinToString(separator = "\n")}",
            )
        }
    }

    /**
     * Upload the file from `recordsData` to S3 and simplify the filename as <partId>.<extension>.
     *
     * @return the uploaded filename, which is different from the serialized buffer filename
     * </extension></partId>
     */
    @Throws(IOException::class)
    private fun loadDataIntoBucket(objectPath: String, recordsData: SerializableBuffer): String {
        val partSize: Long = DEFAULT_PART_SIZE.toLong()
        val bucket: String? = s3Config.bucketName
        val partId: String = getPartId(objectPath)
        val fileExtension: String = getExtension(recordsData.filename)
        val fullObjectKey: String =
            if (!s3Config.fileNamePattern.isNullOrBlank()) {
                s3FilenameTemplateManager.applyPatternToFilename(
                    S3FilenameTemplateParameterObject.builder()
                        .partId(partId)
                        .recordsData(recordsData)
                        .objectPath(objectPath)
                        .fileExtension(fileExtension)
                        .fileNamePattern(s3Config.fileNamePattern)
                        .build(),
                )
            } else {
                objectPath + partId + fileExtension
            }
        val metadata: MutableMap<String, String> = HashMap()
        for (blobDecorator: BlobDecorator in blobDecorators) {
            blobDecorator.updateMetadata(metadata, getMetadataMapping())
        }
        val uploadManager: StreamTransferManager =
            StreamTransferManagerFactory.create(
                    bucket,
                    fullObjectKey,
                    s3Client,
                )
                .setPartSize(partSize)
                .setUserMetadata(metadata)
                .get()
                .checkIntegrity(s3Config.isCheckIntegrity)
                .numUploadThreads(s3Config.uploadThreadsCount)
                .queueCapacity(DEFAULT_QUEUE_CAPACITY)
        var succeeded: Boolean = false

        // Wrap output stream in decorators
        var rawOutputStream: OutputStream = uploadManager.multiPartOutputStreams.first()
        for (blobDecorator: BlobDecorator in blobDecorators) {
            rawOutputStream = blobDecorator.wrap(rawOutputStream)
        }

        try {
            rawOutputStream.use { outputStream ->
                recordsData.inputStream!!.use { dataStream ->
                    dataStream.transferTo(outputStream)
                    succeeded = true
                }
            }
        } catch (e: Exception) {
            logger.error(e) { "Failed to load data into storage $objectPath" }
            throw RuntimeException(e)
        } finally {
            if (!succeeded) {
                uploadManager.abort()
            } else {
                uploadManager.complete()
            }
        }
        if (!s3Client.doesObjectExist(bucket, fullObjectKey)) {
            logger.error { "Failed to upload data into storage, object $fullObjectKey not found" }
            throw RuntimeException("Upload failed")
        }
        val newFilename: String = getFilename(fullObjectKey)
        logger.info {
            "Uploaded buffer file to storage: ${recordsData.filename} -> $fullObjectKey (filename: $newFilename)"
        }
        return newFilename
    }

    /**
     * Users want deterministic file names (e.g. the first file part is really foo-0.csv). Using
     * UUIDs (previous approach) doesn't allow that. However, using pure integers could lead to a
     * collision with an upload from another thread. We also want to be able to continue the same
     * offset between attempts. So, we'll count up the existing files in the directory and use that
     * as a lazy-offset, assuming airbyte manages the dir and has similar naming conventions.
     * `getPartId` will be 0-indexed.
     */
    @VisibleForTesting
    @Synchronized
    fun getPartId(objectPath: String): String {
        val partCount: AtomicInteger =
            partCounts.computeIfAbsent(
                objectPath,
            ) {
                AtomicInteger(0)
            }

        if (partCount.get() == 0) {
            var objects: ObjectListing?
            var objectCount = 0

            val bucket: String? = s3Config.bucketName
            objects = s3Client.listObjects(bucket, objectPath)

            if (objects != null) {
                objectCount += objects.objectSummaries.size
                while (objects != null && objects.nextMarker != null) {
                    objects =
                        s3Client.listObjects(
                            ListObjectsRequest()
                                .withBucketName(bucket)
                                .withPrefix(objectPath)
                                .withMarker(objects.nextMarker),
                        )
                    if (objects != null) {
                        objectCount += objects.objectSummaries.size
                    }
                }
            }

            partCount.set(objectCount)
        }

        return partCount.getAndIncrement().toString()
    }

    override fun dropBucketObject(objectPath: String) {
        cleanUpBucketObject(objectPath, listOf())
    }

    override fun cleanUpBucketObject(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    ) {
        val bucket: String? = s3Config.bucketName
        var objects: ObjectListing =
            s3Client.listObjects(
                ListObjectsRequest()
                    .withBucketName(bucket)
                    .withPrefix(
                        objectPath,
                    ) // pathFormat may use subdirectories under the objectPath to organize files
                    // so we need to recursively list them and filter files matching the pathFormat
                    .withDelimiter(""),
            )
        val regexFormat: Pattern =
            Pattern.compile(getRegexFormat(namespace, streamName, pathFormat))
        while (objects.objectSummaries.size > 0) {
            val keysToDelete: List<DeleteObjectsRequest.KeyVersion> =
                objects.objectSummaries
                    .filter { obj: S3ObjectSummary ->
                        regexFormat
                            .matcher(
                                obj.key,
                            )
                            .matches()
                    }
                    .map { obj: S3ObjectSummary ->
                        DeleteObjectsRequest.KeyVersion(
                            obj.key,
                        )
                    }

            cleanUpObjects(bucket, keysToDelete)
            logger.info {
                "Storage bucket $objectPath has been cleaned-up (${keysToDelete.size} objects matching $regexFormat were deleted)..."
            }
            if (objects.isTruncated) {
                objects = s3Client.listNextBatchOfObjects(objects)
            } else {
                break
            }
        }
    }

    fun getRegexFormat(namespace: String?, streamName: String, pathFormat: String): String {
        val namespaceStr: String = nameTransformer.getNamespace(namespace ?: "")
        val streamNameStr: String = nameTransformer.getIdentifier(streamName)
        return nameTransformer.applyDefaultCase(
            (pathFormat
                .replace(Pattern.quote(FORMAT_VARIABLE_NAMESPACE).toRegex(), namespaceStr)
                .replace(Pattern.quote(FORMAT_VARIABLE_STREAM_NAME).toRegex(), streamNameStr)
                .replace(Pattern.quote(FORMAT_VARIABLE_YEAR).toRegex(), "[0-9]{4}")
                .replace(Pattern.quote(FORMAT_VARIABLE_MONTH).toRegex(), "[0-9]{2}")
                .replace(Pattern.quote(FORMAT_VARIABLE_DAY).toRegex(), "[0-9]{2}")
                .replace(Pattern.quote(FORMAT_VARIABLE_HOUR).toRegex(), "[0-9]{2}")
                .replace(Pattern.quote(FORMAT_VARIABLE_MINUTE).toRegex(), "[0-9]{2}")
                .replace(Pattern.quote(FORMAT_VARIABLE_SECOND).toRegex(), "[0-9]{2}")
                .replace(Pattern.quote(FORMAT_VARIABLE_MILLISECOND).toRegex(), "[0-9]{4}")
                .replace(Pattern.quote(FORMAT_VARIABLE_EPOCH).toRegex(), "[0-9]+")
                .replace(Pattern.quote(FORMAT_VARIABLE_UUID).toRegex(), ".*")
                .replace("/+".toRegex(), "/") // match part_id and extension at the end
            + ".*"),
        )
    }

    override fun cleanUpBucketObject(objectPath: String, stagedFiles: List<String>) {
        val bucket: String? = s3Config.bucketName
        var objects: ObjectListing = s3Client.listObjects(bucket, objectPath)
        while (objects.objectSummaries.size > 0) {
            val keysToDelete: List<DeleteObjectsRequest.KeyVersion> =
                objects.objectSummaries
                    .filter { obj: S3ObjectSummary ->
                        stagedFiles.isEmpty() ||
                            stagedFiles.contains(
                                obj.key,
                            )
                    }
                    .map { obj: S3ObjectSummary ->
                        DeleteObjectsRequest.KeyVersion(
                            obj.key,
                        )
                    }

            cleanUpObjects(bucket, keysToDelete)
            logger.info {
                "Storage bucket $objectPath has been cleaned-up (${keysToDelete.size} objects were deleted)..."
            }
            if (objects.isTruncated) {
                objects = s3Client.listNextBatchOfObjects(objects)
            } else {
                break
            }
        }
    }

    protected open fun cleanUpObjects(
        bucket: String?,
        keysToDelete: List<DeleteObjectsRequest.KeyVersion>
    ) {
        if (keysToDelete.isNotEmpty()) {
            logger.info {
                "Deleting objects ${keysToDelete.map { obj: DeleteObjectsRequest.KeyVersion -> obj.key }
                .joinToString(separator = ", ")}"
            }
            s3Client.deleteObjects(DeleteObjectsRequest(bucket).withKeys(keysToDelete))
        }
    }

    override fun isValidData(jsonNode: JsonNode): Boolean {
        return true
    }

    override fun getMetadataMapping(): Map<String, String> {
        return ImmutableMap.of(
            AesCbcEnvelopeEncryptionBlobDecorator.ENCRYPTED_CONTENT_ENCRYPTING_KEY,
            "x-amz-key",
            AesCbcEnvelopeEncryptionBlobDecorator.INITIALIZATION_VECTOR,
            "x-amz-iv",
        )
    }

    fun uploadManifest(manifestFilePath: String, manifestContents: String) {
        s3Client.putObject(s3Config.bucketName, manifestFilePath, manifestContents)
    }

    companion object {
        const val DEFAULT_UPLOAD_THREADS: Int = 10 // The S3 cli uses 10 threads by default.
        const val R2_UPLOAD_THREADS: Int = 3

        private const val DEFAULT_QUEUE_CAPACITY: Int = DEFAULT_UPLOAD_THREADS
        private const val DEFAULT_PART_SIZE: Int = 10
        private const val UPLOAD_RETRY_LIMIT: Int = 3
        private const val FORMAT_VARIABLE_NAMESPACE: String = "\${NAMESPACE}"
        private const val FORMAT_VARIABLE_STREAM_NAME: String = "\${STREAM_NAME}"
        private const val FORMAT_VARIABLE_YEAR: String = "\${YEAR}"
        private const val FORMAT_VARIABLE_MONTH: String = "\${MONTH}"
        private const val FORMAT_VARIABLE_DAY: String = "\${DAY}"
        private const val FORMAT_VARIABLE_HOUR: String = "\${HOUR}"
        private const val FORMAT_VARIABLE_MINUTE: String = "\${MINUTE}"
        private const val FORMAT_VARIABLE_SECOND: String = "\${SECOND}"
        private const val FORMAT_VARIABLE_MILLISECOND: String = "\${MILLISECOND}"
        private const val FORMAT_VARIABLE_EPOCH: String = "\${EPOCH}"
        private const val FORMAT_VARIABLE_UUID: String = "\${UUID}"
        private const val GZ_FILE_EXTENSION: String = "gz"
        @VisibleForTesting
        @JvmStatic
        fun getFilename(fullPath: String): String {
            return fullPath.substring(fullPath.lastIndexOf("/") + 1)
        }

        @VisibleForTesting
        @JvmStatic
        fun getExtension(filename: String): String {
            val result: String = FilenameUtils.getExtension(filename)
            if (result.isBlank()) {
                return result
            } else if ((GZ_FILE_EXTENSION == result)) {
                return getExtension(
                    filename.substring(
                        0,
                        filename.length - 3,
                    ),
                ) + "." + GZ_FILE_EXTENSION
            }
            return ".$result"
        }
    }
}
