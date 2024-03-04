package io.airbyte.integrations.destination.s3.util

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.*
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryptionBlobDecorator
import io.airbyte.cdk.integrations.destination.s3.BlobStorageOperations
import io.airbyte.cdk.integrations.destination.s3.template.S3FilenameTemplateParameterObject
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.string.Strings.join
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.core.util.StringUtils
import jakarta.inject.Singleton
import org.apache.commons.io.FilenameUtils
import org.joda.time.DateTime
import java.io.IOException
import java.io.OutputStream
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.regex.Pattern

private val logger = KotlinLogging.logger {}

@Singleton
class S3StorageOperations(
    private val s3ConnectorConfiguration: S3ConnectorConfiguration,
    private val s3NameTransformer: S3NameTransformer,
    private val amazonS3Client: AmazonS3,
    private val s3FilenameTemplateManager: S3FilenameTemplateManager,
): BlobStorageOperations() {

    private val partCounts: ConcurrentMap<String, AtomicInteger> = ConcurrentHashMap()

    companion object {
        private const val DEFAULT_PART_SIZE = 10
        const val DEFAULT_UPLOAD_THREADS: Int = 10 // The S3 cli uses 10 threads by default.
        const val R2_UPLOAD_THREADS: Int = 3
        private const val DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS
        private const val FORMAT_VARIABLE_NAMESPACE = "\${NAMESPACE}"
        private const val FORMAT_VARIABLE_STREAM_NAME = "\${STREAM_NAME}"
        private const val FORMAT_VARIABLE_YEAR = "\${YEAR}"
        private const val FORMAT_VARIABLE_MONTH = "\${MONTH}"
        private const val FORMAT_VARIABLE_DAY = "\${DAY}"
        private const val FORMAT_VARIABLE_HOUR = "\${HOUR}"
        private const val FORMAT_VARIABLE_MINUTE = "\${MINUTE}"
        private const val FORMAT_VARIABLE_SECOND = "\${SECOND}"
        private const val FORMAT_VARIABLE_MILLISECOND = "\${MILLISECOND}"
        private const val FORMAT_VARIABLE_EPOCH = "\${EPOCH}"
        private const val FORMAT_VARIABLE_UUID = "\${UUID}"
        private const val GZ_FILE_EXTENSION = "gz"
        private const val UPLOAD_RETRY_LIMIT = 3
    }

    override fun getBucketObjectPath(
        namespace: String?,
        streamName: String,
        writeDatetime: DateTime,
        customPathFormat: String
    ): String {
        val namespaceStr: String = s3NameTransformer.getNamespace(if (StringUtils.isNotEmpty(namespace)) namespace else "")
        val streamNameStr: String = s3NameTransformer.getIdentifier(streamName)
        return s3NameTransformer.applyDefaultCase(
            customPathFormat
                .replace(Pattern.quote(FORMAT_VARIABLE_NAMESPACE).toRegex(), namespaceStr)
                .replace(Pattern.quote(FORMAT_VARIABLE_STREAM_NAME).toRegex(), streamNameStr)
                .replace(Pattern.quote(FORMAT_VARIABLE_YEAR).toRegex(), String.format("%s", writeDatetime.year().get())
                .replace(Pattern.quote(FORMAT_VARIABLE_MONTH).toRegex(), String.format("%02d", writeDatetime.monthOfYear().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_DAY).toRegex(), String.format("%02d", writeDatetime.dayOfMonth().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_HOUR).toRegex(), String.format("%02d", writeDatetime.hourOfDay().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_MINUTE).toRegex(), String.format("%02d", writeDatetime.minuteOfHour().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_SECOND).toRegex(), String.format("%02d", writeDatetime.secondOfMinute().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_MILLISECOND).toRegex(), String.format("%04d", writeDatetime.millisOfSecond().get()))
                .replace(Pattern.quote(FORMAT_VARIABLE_EPOCH).toRegex(), String.format("%d", writeDatetime.millis))
                .replace(Pattern.quote(FORMAT_VARIABLE_UUID).toRegex(), String.format("%s", UUID.randomUUID()))
                .replace("/+".toRegex(), "/"))
        )
    }

    override fun createBucketIfNotExists() {
        val bucket: String? = s3ConnectorConfiguration.s3BucketName
        if (!amazonS3Client.doesBucketExistV2(bucket)) {
            logger.info { "Bucket $bucket does not exist; creating..." }
            amazonS3Client.createBucket(bucket)
            logger.info { "Bucket $bucket has been created." }
        }
    }

    override fun uploadRecordsToBucket(
        recordsData: SerializableBuffer,
        namespace: String,
        objectPath: String
    ): String {
        val exceptionsThrown: MutableList<Exception?> = ArrayList()
        while (exceptionsThrown.size < UPLOAD_RETRY_LIMIT) {
            if (exceptionsThrown.isNotEmpty()) {
                logger.info { "Retrying to upload records into storage $objectPath (${exceptionsThrown.size}/$UPLOAD_RETRY_LIMIT)" }
            }

            try {
                val fileName: String = loadDataIntoBucket(objectPath, recordsData)
                logger.info { "Successfully loaded records to stage $objectPath with ${exceptionsThrown.size} re-attempt(s)" }
                return fileName
            } catch (e: Exception) {
                logger.error(e) { "Failed to upload records into storage $objectPath" }
                exceptionsThrown.add(e)
            }
        }


        // Verifying that ALL exceptions are authentication related before assuming this is a configuration
        // issue reduces risk of misidentifying errors or reporting a transient error.
        val areAllExceptionsAuthExceptions =
            exceptionsThrown.stream().filter { e: Exception? -> e is AmazonS3Exception }
                .map { s3e: Exception? -> (s3e as AmazonS3Exception?)!!.statusCode }
                .filter { o: Int? ->
                    ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(o)
                }
                .count() == exceptionsThrown.size.toLong()
        if (areAllExceptionsAuthExceptions) {
            throw ConfigErrorException(exceptionsThrown[0]!!.message, exceptionsThrown[0])
        } else {
            throw RuntimeException("Exceptions thrown while uploading records into storage: ${join(exceptionsThrown, "\n")}")
        }
    }

    override fun cleanUpBucketObject(objectPath: String, stagedFiles: List<String>) {
        val bucket: String? = s3ConnectorConfiguration.s3BucketName
        var objects: ObjectListing = amazonS3Client.listObjects(bucket, objectPath)
        while (objects.objectSummaries.size > 0) {
            val keysToDelete = objects.objectSummaries
                .stream()
                .filter { obj: S3ObjectSummary -> stagedFiles.isEmpty() || stagedFiles.contains(obj.key) }
                .map { obj: S3ObjectSummary -> DeleteObjectsRequest.KeyVersion(obj.key) }
                .toList()
            cleanUpObjects(bucket, keysToDelete)
            logger.info { "Storage bucket $objectPath has been cleaned-up (${keysToDelete.size} objects were deleted)..." }
            if (objects.isTruncated) {
                objects = amazonS3Client.listNextBatchOfObjects(objects)
            } else {
                break
            }
        }
    }

    override fun cleanUpBucketObject(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    ) {
        val bucket: String? = s3ConnectorConfiguration.s3BucketName
        var objects: ObjectListing = amazonS3Client.listObjects(
            ListObjectsRequest()
                .withBucketName(bucket)
                .withPrefix(objectPath) // pathFormat may use subdirectories under the objectPath to organize files
                // so we need to recursively list them and filter files matching the pathFormat
                .withDelimiter("")
        )
        val regexFormat = Pattern.compile(getRegexFormat(namespace, streamName, pathFormat))
        while (objects.objectSummaries.size > 0) {
            val keysToDelete = objects.objectSummaries
                .stream()
                .filter { obj: S3ObjectSummary -> regexFormat.matcher(obj.key).matches() }
                .map { obj: S3ObjectSummary -> DeleteObjectsRequest.KeyVersion(obj.key) }
                .toList()
            cleanUpObjects(bucket, keysToDelete)
            logger.info { "Storage bucket $objectPath has been cleaned-up (${keysToDelete.size} objects matching $regexFormat were deleted)..." }
            if (objects.isTruncated) {
                objects = amazonS3Client.listNextBatchOfObjects(objects)
            } else {
                break
            }
        }
    }

    override fun dropBucketObject(objectPath: String) {
        cleanUpBucketObject(objectPath, listOf())
    }

    override fun isValidData(jsonNode: JsonNode?): Boolean {
        return true
    }

    override fun getMetadataMapping(): Map<String, String> {
        return mapOf(
            AesCbcEnvelopeEncryptionBlobDecorator.ENCRYPTED_CONTENT_ENCRYPTING_KEY to  "x-amz-key",
            AesCbcEnvelopeEncryptionBlobDecorator.INITIALIZATION_VECTOR to "x-amz-iv"
        )
    }

    private fun cleanUpObjects(bucket: String?, keysToDelete: List<DeleteObjectsRequest.KeyVersion>) {
        if (keysToDelete.isNotEmpty()) {
            logger.info { "Deleting objects ${java.lang.String.join(", ", keysToDelete.stream().map { obj: DeleteObjectsRequest.KeyVersion -> obj.key }.toList())}" }
            amazonS3Client.deleteObjects(DeleteObjectsRequest(bucket).withKeys(keysToDelete))
        }
    }

    private fun getRegexFormat(namespace: String?, streamName: String?, pathFormat: String): String {
            val namespaceStr: String = s3NameTransformer.getNamespace(if (StringUtils.isNotEmpty(namespace)) namespace else "")
            val streamNameStr: String = s3NameTransformer.getIdentifier(streamName)
            return s3NameTransformer.applyDefaultCase(
                pathFormat
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
                        + ".*")
    }

    /**
     * Upload the file from `recordsData` to S3 and simplify the filename as <partId>.<extension>.
     *
     * @return the uploaded filename, which is different from the serialized buffer filename
    </extension></partId> */
    @Throws(IOException::class)
    private fun loadDataIntoBucket(objectPath: String, recordsData: SerializableBuffer): String {
        val partSize = DEFAULT_PART_SIZE.toLong()
        val bucket: String? = s3ConnectorConfiguration.s3BucketName
        val partId: String = getPartId(objectPath)
        val fileExtension = getExtension(recordsData.filename)
        val fullObjectKey = if (StringUtils.isNotEmpty(s3ConnectorConfiguration.fileNamePattern)) {
            s3FilenameTemplateManager
                .applyPatternToFilename(
                    S3FilenameTemplateParameterObject
                        .builder()
                        .partId(partId)
                        .recordsData(recordsData)
                        .objectPath(objectPath)
                        .fileExtension(fileExtension)
                        .fileNamePattern(s3ConnectorConfiguration.fileNamePattern)
                        .build()
                )
        } else {
            objectPath + partId + fileExtension
        }
        val metadata: Map<String, String> = HashMap()
        for (blobDecorator in blobDecorators) {
            blobDecorator.updateMetadata(metadata, metadataMapping)
        }
        val uploadManager = StreamTransferManagerFactory.create(bucket, fullObjectKey, amazonS3Client)
            .setPartSize(partSize)
            .setUserMetadata(metadata)
            .get()
            .checkIntegrity(true)
            .numUploadThreads(DEFAULT_UPLOAD_THREADS)
            .queueCapacity(DEFAULT_QUEUE_CAPACITY)
        var succeeded = false

        // Wrap output stream in decorators
        var rawOutputStream: OutputStream = uploadManager.multiPartOutputStreams[0]
        for (blobDecorator in blobDecorators) {
            rawOutputStream = blobDecorator.wrap(rawOutputStream)
        }

        try {
            rawOutputStream.use { outputStream ->
                recordsData.inputStream.use { dataStream ->
                    dataStream.transferTo(outputStream)
                    succeeded = true
                }
            }
        } catch (e: Exception) {
            logger.error(e) { "Failed to load data into storage $objectPath" }
            throw java.lang.RuntimeException(e)
        } finally {
            if (!succeeded) {
                uploadManager.abort()
            } else {
                uploadManager.complete()
            }
        }
        if (!amazonS3Client.doesObjectExist(bucket, fullObjectKey)) {
            logger.error { "Failed to upload data into storage, object $fullObjectKey not found" }
            throw RuntimeException("Upload failed")
        }
        val newFilename = getFilename(fullObjectKey)
        logger.info { "Uploaded buffer file to storage: ${recordsData.filename} -> $fullObjectKey (filename: $newFilename)" }
        return newFilename
    }

    private fun getFilename(fullPath: String): String {
        return fullPath.substring(fullPath.lastIndexOf("/") + 1)
    }

    private fun getExtension(filename: String): String {
        val result = FilenameUtils.getExtension(filename)
        if (result.isBlank()) {
            return result
        } else if (GZ_FILE_EXTENSION == result) {
            return "${getExtension(filename.substring(0, filename.length - 3))}.${GZ_FILE_EXTENSION}"
        }
        return ".$result"
    }

    /**
     * Users want deterministic file names (e.g. the first file part is really foo-0.csv). Using UUIDs
     * (previous approach) doesn't allow that. However, using pure integers could lead to a collision
     * with an upload from another thread. We also want to be able to continue the same offset between
     * attempts. So, we'll count up the existing files in the directory and use that as a lazy-offset,
     * assuming airbyte manages the dir and has similar naming conventions. `getPartId` will be
     * 0-indexed.
     */
    @Synchronized
    private fun getPartId(objectPath: String?): String {
        val partCount: AtomicInteger = partCounts.computeIfAbsent(objectPath) { AtomicInteger(0) }

        if (partCount.get() == 0) {
            var objects: ObjectListing
            var objectCount = 0

            val bucket: String? = s3ConnectorConfiguration.s3BucketName
            objects = amazonS3Client.listObjects(bucket, objectPath)

            objectCount += objects.objectSummaries.size
            while (objects.nextMarker != null) {
                objects = amazonS3Client.listObjects(
                    ListObjectsRequest().withBucketName(bucket).withPrefix(objectPath)
                        .withMarker(objects.nextMarker)
                )
                objectCount += objects.objectSummaries.size
            }

            partCount.set(objectCount)
        }

        return partCount.getAndIncrement().toString()
    }
}