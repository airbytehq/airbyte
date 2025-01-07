/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.s3

import aws.sdk.kotlin.services.s3.model.CompleteMultipartUploadRequest
import aws.sdk.kotlin.services.s3.model.CompletedMultipartUpload
import aws.sdk.kotlin.services.s3.model.CompletedPart
import aws.sdk.kotlin.services.s3.model.CreateMultipartUploadResponse
import aws.sdk.kotlin.services.s3.model.UploadPartRequest
import aws.smithy.kotlin.runtime.content.ByteStream
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.apache.mina.util.ConcurrentHashSet

/**
 * An S3MultipartUpload that provides an [OutputStream] abstraction for writing data. This should
 * never be created directly, but used indirectly through [S3Client.streamingUpload].
 *
 * NOTE: The OutputStream interface does not support suspending functions, but the kotlin s3 SDK
 * does. To stitch them together, we could use `runBlocking`, but that would risk blocking the
 * thread (and defeating the purpose of using the kotlin sdk). In order to avoid this, we use a
 * [Channel] to queue up work and process it a coroutine, launched asynchronously in the same
 * context. The work will be coherent as long as the calls to the interface are made synchronously
 * (which would be the case without coroutines).
 */
class S3MultipartUpload<T : OutputStream>(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    private val response: CreateMultipartUploadResponse,
    private val underlyingBuffer: ByteArrayOutputStream,
    private val streamProcessor: StreamProcessor<T>,
    uploadConfig: ObjectStorageUploadConfiguration?,
) {
    private val log = KotlinLogging.logger {}
    private val partSize =
        uploadConfig?.uploadPartSizeBytes
            ?: throw IllegalStateException("Streaming upload part size is not configured")
    private val wrappingBuffer = streamProcessor.wrapper(underlyingBuffer)
    private val partQueue = Channel<ByteArray>(Channel.UNLIMITED)
    private val isClosed = AtomicBoolean(false)

    /**
     * Run the upload using the provided block. This should only be used by the
     * [S3Client.streamingUpload] method. Completed partss are processed asynchronously in the
     * [launch] block. The for loop will suspend until [partQueue] is closed, after which the call
     * to [complete] will finish the upload.
     *
     * Moreover, [runUsing] will not return until the launch block exits. This ensures
     * - parts are processed in order
     * - minimal work is done in [runBlocking] (just enough to enqueue the parts, and only once per
     * part)
     * - the upload will not complete until the [OutputStream.close] is called (either by the user
     * in [block] or when the [use] block terminates).
     * - the upload will not complete until all the work is done
     */
    suspend fun runUsing(block: suspend (OutputStream) -> Unit) = coroutineScope {
        log.info {
            "Starting multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
        }
        launch {
            val uploadedParts = mutableListOf<CompletedPart>()
            for (bytes in partQueue) {
                val part = uploadPart(bytes, uploadedParts)
                uploadedParts.add(part)
            }
            streamProcessor.partFinisher.invoke(wrappingBuffer)
            if (underlyingBuffer.size() > 0) {
                val part = uploadPart(underlyingBuffer.toByteArray(), uploadedParts)
                uploadedParts.add(part)
            }
            complete(uploadedParts)
        }
        UploadStream().use { block(it) }
        log.info {
            "Completed multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
        }
    }

    inner class UploadStream : OutputStream() {
        override fun close() {
            if (isClosed.setOnce()) {
                partQueue.close()
            }
        }

        override fun flush() = wrappingBuffer.flush()

        override fun write(b: Int) {
            wrappingBuffer.write(b)
            if (underlyingBuffer.size() >= partSize) {
                enqueuePart()
            }
        }

        override fun write(b: ByteArray) {
            wrappingBuffer.write(b)
            if (underlyingBuffer.size() >= partSize) {
                enqueuePart()
            }
        }
    }

    private fun enqueuePart() {
        wrappingBuffer.flush()
        val bytes = underlyingBuffer.toByteArray()
        underlyingBuffer.reset()
        runBlocking { partQueue.send(bytes) }
    }

    private suspend fun uploadPart(
        bytes: ByteArray,
        uploadedParts: List<CompletedPart>
    ): CompletedPart {
        val partNumber = uploadedParts.size + 1
        val request = UploadPartRequest {
            uploadId = response.uploadId
            bucket = response.bucket
            key = response.key
            body = ByteStream.fromBytes(bytes)
            this.partNumber = partNumber
        }
        val uploadResponse = client.uploadPart(request)
        return CompletedPart {
            this.partNumber = partNumber
            this.eTag = uploadResponse.eTag
        }
    }

    private suspend fun complete(uploadedParts: List<CompletedPart>) {
        val request = CompleteMultipartUploadRequest {
            uploadId = response.uploadId
            bucket = response.bucket
            key = response.key
            this.multipartUpload = CompletedMultipartUpload { parts = uploadedParts }
        }
        client.completeMultipartUpload(request)
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class S3StreamingUpload(
    private val client: aws.sdk.kotlin.services.s3.S3Client,
    private val bucketConfig: S3BucketConfiguration,
    private val response: CreateMultipartUploadResponse,
) : StreamingUpload<S3Object> {
    private val log = KotlinLogging.logger {}
    private val uploadedParts = ConcurrentHashSet<CompletedPart>()
    private val isComplete = AtomicBoolean(false)

    override suspend fun uploadPart(part: ByteArray, index: Int) {
        log.info { "Uploading part $index to ${response.key} (uploadId=${response.uploadId}" }

        try {
            val request = UploadPartRequest {
                uploadId = response.uploadId
                bucket = response.bucket
                key = response.key
                body = ByteStream.fromBytes(part)
                this.partNumber = index
            }
            val uploadResponse = client.uploadPart(request)
            uploadedParts.add(
                CompletedPart {
                    this.partNumber = index
                    this.eTag = uploadResponse.eTag
                }
            )
        } catch (e: Exception) {
            log.error(e) {
                "Failed to upload part $index to ${response.key} (uploadId=${response.uploadId}"
            }
            throw e
        }
    }

    override suspend fun complete(): S3Object {
        try {
            if (isComplete.setOnce()) {
                log.info {
                    "Completing multipart upload to ${response.key} (uploadId=${response.uploadId}"
                }
                val partsSorted = uploadedParts.toList().sortedBy { it.partNumber }
                if (partsSorted.isEmpty()) {
                    log.warn {
                        "Skipping empty upload to ${response.key} (uploadId=${response.uploadId}"
                    }
                    return S3Object(response.key!!, bucketConfig)
                }

                val request = CompleteMultipartUploadRequest {
                    uploadId = response.uploadId
                    bucket = response.bucket
                    key = response.key
                    this.multipartUpload = CompletedMultipartUpload { parts = partsSorted }
                }
                // S3 will handle enforcing no gaps in the part numbers
                client.completeMultipartUpload(request)
            } else {
                log.warn {
                    "Complete called multiple times for ${response.key} (uploadId=${response.uploadId}"
                }
            }
        } catch (e: Exception) {
            log.error(e) {
                "Failed to complete upload to ${response.key} (uploadId=${response.uploadId}; parts=${uploadedParts.map {it.partNumber}.sortedBy { it }}"
            }
            throw e
        }

        return S3Object(response.key!!, bucketConfig)
    }
}
