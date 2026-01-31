/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.fasterxml.jackson.databind.JsonNode
import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.cloud.storage.BlobId
import com.google.cloud.storage.BlobInfo
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.BlobStorageOperations
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.nio.channels.Channels
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.regex.Pattern
import org.joda.time.DateTime

private val logger = KotlinLogging.logger {}

class GcsNativeStorageOperations(
    private val nameTransformer: NamingConventionTransformer,
    private val storage: Storage,
    private val bucketName: String,
    private val bucketPath: String?
) : BlobStorageOperations() {

    private val partCounts: ConcurrentMap<String, AtomicInteger> = ConcurrentHashMap()
    private val objectNameByPrefix: ConcurrentMap<String, Set<String>> = ConcurrentHashMap()

    companion object {
        private const val UPLOAD_RETRY_LIMIT = 3
        private const val GENERATION_ID_USER_META_KEY = "ab-generation-id"

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

        fun createStorageClient(serviceAccountJson: String): Storage {
            val credentials: GoogleCredentials =
                ServiceAccountCredentials.fromStream(
                    ByteArrayInputStream(serviceAccountJson.toByteArray())
                )
            return StorageOptions.newBuilder().setCredentials(credentials).build().service
        }
    }

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

    override fun createBucketIfNotExists() {
        val bucket = storage.get(bucketName)
        if (bucket == null) {
            logger.info { "Bucket $bucketName does not exist; creating..." }
            storage.create(com.google.cloud.storage.BucketInfo.of(bucketName))
            logger.info { "Bucket $bucketName has been created." }
        }
    }

    override fun uploadRecordsToBucket(
        recordsData: SerializableBuffer,
        namespace: String?,
        objectPath: String,
        generationId: Long
    ): String {
        val exceptionsThrown: MutableList<Exception> = ArrayList()
        while (exceptionsThrown.size < UPLOAD_RETRY_LIMIT) {
            if (exceptionsThrown.isNotEmpty()) {
                logger.info {
                    "Retrying to upload records into storage $objectPath (${exceptionsThrown.size}/$UPLOAD_RETRY_LIMIT)"
                }
            }

            try {
                val fileName: String = loadDataIntoBucket(objectPath, recordsData, generationId)
                logger.info {
                    "Successfully loaded records to stage $objectPath with ${exceptionsThrown.size} re-attempt(s)"
                }
                return fileName
            } catch (e: Exception) {
                logger.error(e) { "Failed to upload records into storage $objectPath" }
                exceptionsThrown.add(e)
            }
        }
        throw RuntimeException(
            "Exceptions thrown while uploading records into storage: ${exceptionsThrown.joinToString(separator = "\n")}",
        )
    }

    private fun loadDataIntoBucket(
        objectPath: String,
        recordsData: SerializableBuffer,
        generationId: Long
    ): String {
        val partId: String = getPartId(objectPath)
        val fileExtension: String = getExtension(recordsData.filename)
        val fullObjectKey = objectPath + partId + fileExtension

        val metadata: MutableMap<String, String?> = HashMap()
        metadata[GENERATION_ID_USER_META_KEY] = generationId.toString()

        val blobId = BlobId.of(bucketName, fullObjectKey)
        val blobInfo = BlobInfo.newBuilder(blobId).setMetadata(metadata).build()

        recordsData.inputStream!!.use { inputStream ->
            val writer = storage.writer(blobInfo)
            Channels.newOutputStream(writer).use { outputStream ->
                inputStream.transferTo(outputStream)
            }
        }

        val newFilename: String = getFilename(fullObjectKey)
        logger.info {
            "Uploaded buffer file to storage: ${recordsData.filename} -> $fullObjectKey (filename: $newFilename)"
        }
        return newFilename
    }

    @Synchronized
    private fun getPartId(objectPath: String): String {
        val partCount: AtomicInteger = partCounts.computeIfAbsent(objectPath) { AtomicInteger(0) }
        objectNameByPrefix.computeIfAbsent(objectPath) {
            val objectList = mutableSetOf<String>()
            val blobs = storage.list(bucketName, Storage.BlobListOption.prefix(objectPath))
            for (blob in blobs.iterateAll()) {
                objectList.add(blob.name)
            }
            objectList
        }
        return partCount.getAndIncrement().toString()
    }

    private fun getExtension(filename: String?): String {
        if (filename == null) return ""
        val lastDot = filename.lastIndexOf('.')
        return if (lastDot >= 0) filename.substring(lastDot) else ""
    }

    private fun getFilename(fullObjectKey: String): String {
        val lastSlash = fullObjectKey.lastIndexOf('/')
        return if (lastSlash >= 0) fullObjectKey.substring(lastSlash + 1) else fullObjectKey
    }

    override fun cleanUpBucketObject(objectPath: String, stagedFiles: List<String>) {
        val blobs = storage.list(bucketName, Storage.BlobListOption.prefix(objectPath))
        for (blob in blobs.iterateAll()) {
            if (stagedFiles.isEmpty() || stagedFiles.contains(blob.name)) {
                logger.info { "Deleting object ${blob.name}" }
                storage.delete(BlobId.of(bucketName, blob.name))
            }
        }
        logger.info { "Storage bucket $objectPath has been cleaned-up..." }
    }

    override fun cleanUpBucketObject(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    ) {
        val regexFormat: Pattern =
            Pattern.compile(getRegexFormat(namespace, streamName, pathFormat))
        val blobs = storage.list(bucketName, Storage.BlobListOption.prefix(objectPath))
        var deletedCount = 0
        for (blob in blobs.iterateAll()) {
            if (regexFormat.matcher(blob.name).matches()) {
                logger.info { "Deleting object ${blob.name}" }
                storage.delete(BlobId.of(bucketName, blob.name))
                deletedCount++
            }
        }
        logger.info {
            "Storage bucket $objectPath has been cleaned-up ($deletedCount objects matching $regexFormat were deleted)..."
        }
    }

    override fun cleanUpObjects(keysToDelete: List<String>) {
        for (key in keysToDelete) {
            logger.info { "Deleting object $key" }
            storage.delete(BlobId.of(bucketName, key))
        }
    }

    override fun listExistingObjects(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String,
        currentGenerationId: Long?
    ): List<String> {
        val regexFormat: Pattern =
            Pattern.compile(getRegexFormat(namespace, streamName, pathFormat))
        val result = mutableListOf<String>()
        val blobs = storage.list(bucketName, Storage.BlobListOption.prefix(objectPath))
        for (blob in blobs.iterateAll()) {
            if (regexFormat.matcher(blob.name).matches()) {
                if (currentGenerationId != null) {
                    val genIdStr = blob.metadata?.get(GENERATION_ID_USER_META_KEY)
                    if (genIdStr != null) {
                        try {
                            val genId = genIdStr.toLong()
                            if (genId < currentGenerationId) {
                                result.add(blob.name)
                            }
                        } catch (e: NumberFormatException) {
                            result.add(blob.name)
                        }
                    } else {
                        result.add(blob.name)
                    }
                } else {
                    result.add(blob.name)
                }
            }
        }
        return result
    }

    override fun dropBucketObject(objectPath: String) {
        cleanUpBucketObject(objectPath, listOf())
    }

    override fun isValidData(jsonNode: JsonNode): Boolean {
        return true
    }

    override fun getMetadataMapping(): Map<String, String> {
        return HashMap()
    }

    override fun getStageGeneration(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    ): Long? {
        val regexFormat: Pattern =
            Pattern.compile(getRegexFormat(namespace, streamName, pathFormat))
        var lastModifiedBlob: com.google.cloud.storage.Blob? = null
        val blobs = storage.list(bucketName, Storage.BlobListOption.prefix(objectPath))
        for (blob in blobs.iterateAll()) {
            if (regexFormat.matcher(blob.name).matches()) {
                if (
                    lastModifiedBlob == null ||
                        (blob.updateTimeOffsetDateTime != null &&
                            lastModifiedBlob.updateTimeOffsetDateTime != null &&
                            blob.updateTimeOffsetDateTime.isAfter(
                                lastModifiedBlob.updateTimeOffsetDateTime
                            ))
                ) {
                    lastModifiedBlob = blob
                }
            }
        }
        if (lastModifiedBlob == null) {
            return null
        }
        val genIdStr = lastModifiedBlob.metadata?.get(GENERATION_ID_USER_META_KEY)
        return genIdStr?.toLongOrNull()
    }

    private fun getRegexFormat(namespace: String?, streamName: String, pathFormat: String): String {
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
                .replace("/+".toRegex(), "/") + ".*"),
        )
    }
}
