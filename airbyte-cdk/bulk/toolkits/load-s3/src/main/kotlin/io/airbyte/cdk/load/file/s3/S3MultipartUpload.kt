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

    suspend fun run(block: suspend (OutputStream) -> Unit) = coroutineScope {
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
    }

    private suspend fun complete() {
        if (underlyingBuffer.size() > 0) {
            uploadPart()
        }
        log.info {
            "Completing multipart upload to ${response.bucket}/${response.key} (${response.uploadId}"
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
