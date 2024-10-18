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
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.io.Writer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.channels.Channel
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

    private val work = Channel<suspend () -> Unit>(Channel.UNLIMITED)

    suspend fun start(): Job =
        CoroutineScope(Dispatchers.IO).launch {
            for (unit in work) {
                uploadPart()
            }
            completeInner()
        }

    inner class UploadWriter : Writer() {
        override fun close() {
            log.warn { "Close called on UploadWriter, ignoring." }
        }

        override fun flush() {
            throw NotImplementedError("flush() is not supported on S3MultipartUpload.UploadWriter")
        }

        override fun write(str: String) {
            wrappingBuffer.write(str.toByteArray(Charsets.UTF_8))
            if (underlyingBuffer.size() >= partSize) {
                runBlocking { work.send { uploadPart() } }
            }
        }

        override fun write(cbuf: CharArray, off: Int, len: Int) {
            write(String(cbuf, off, len))
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

    suspend fun complete() {
        work.close()
    }

    private suspend fun completeInner() {
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
