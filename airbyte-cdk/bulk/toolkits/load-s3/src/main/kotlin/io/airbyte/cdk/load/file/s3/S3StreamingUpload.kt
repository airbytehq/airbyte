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
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean
import org.apache.mina.util.ConcurrentHashSet

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
