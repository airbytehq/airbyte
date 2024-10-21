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
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

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

    private val uploadedParts = mutableListOf<CompletedPart>()
    private val partSize =
        uploadConfig?.streamingUploadPartSize
            ?: throw IllegalStateException("Streaming upload part size is not configured")
    private val wrappingBuffer = streamProcessor.wrapper(underlyingBuffer)
    private val workQueue = Channel<suspend () -> Unit>(Channel.UNLIMITED)
    private val closeOnce = AtomicBoolean(false)

    /**
     * Run the upload using the provided block. This should only be used by the
     * [S3Client.streamingUpload] method. Work items are processed asynchronously in the [launch]
     * block. The for loop will suspend until [workQueue] is closed, after which the call to
     * [complete] will finish the upload.
     *
     * Moreover, [runUsing] will not return until the launch block exits. This ensures
     * - work items are processed in order
     * - minimal work is done in [runBlocking] (just enough to enqueue the work items)
     * - the upload will not complete until the [OutputStream.close] is called (either by the user
     * in [block] or when the [use] block terminates).
     * - the upload will not complete until all the work is done
     */
    suspend fun runUsing(block: suspend (OutputStream) -> Unit) = coroutineScope {
        log.info {
            "Starting multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
        }
        launch {
            for (item in workQueue) {
                item()
            }
            complete()
        }
        UploadStream().use { block(it) }
        log.info {
            "Completed multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
        }
    }

    inner class UploadStream : OutputStream() {
        override fun close() = runBlocking {
            workQueue.send {
                if (closeOnce.setOnce()) {
                    workQueue.close()
                }
            }
        }

        override fun flush() = runBlocking { workQueue.send { wrappingBuffer.flush() } }

        override fun write(b: Int) = runBlocking {
            workQueue.send {
                wrappingBuffer.write(b)
                if (underlyingBuffer.size() >= partSize) {
                    uploadPart()
                }
            }
        }

        override fun write(b: ByteArray) = runBlocking {
            workQueue.send {
                println("write[${response.uploadId}](${b.size})")
                wrappingBuffer.write(b)
                if (underlyingBuffer.size() >= partSize) {
                    uploadPart()
                }
            }
        }
    }

    private suspend fun uploadPart() {
        streamProcessor.partFinisher.invoke(wrappingBuffer)
        val partNumber = uploadedParts.size + 1
        println("uploadPart[${response.uploadId}](${partNumber}, size=${underlyingBuffer.size()})")
        val request = UploadPartRequest {
            uploadId = response.uploadId
            bucket = response.bucket
            key = response.key
            body = ByteStream.fromBytes(underlyingBuffer.toByteArray())
            this.partNumber = partNumber
        }
        val uploadResponse = client.uploadPart(request)
        uploadedParts.add(
            CompletedPart {
                this.partNumber = partNumber
                this.eTag = uploadResponse.eTag
            }
        )
        underlyingBuffer.reset()
        println("after reset, size=${underlyingBuffer.size()}")
    }

    private suspend fun complete() {
        println("complete()")
        if (underlyingBuffer.size() > 0) {
            uploadPart()
        }
        val request = CompleteMultipartUploadRequest {
            uploadId = response.uploadId
            bucket = response.bucket
            key = response.key
            this.multipartUpload = CompletedMultipartUpload { parts = uploadedParts }
        }
        client.completeMultipartUpload(request)
    }
}
