/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.util

import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

object StreamTransferManagerFactory {

    // See this doc about how they affect memory usage:
    // https://alexmojaki.github.io/s3-stream-upload/javadoc/apidocs/alex/mojaki/s3upload/StreamTransferManager.html
    // Total memory = (numUploadThreads + queueCapacity) * partSize + numStreams * (partSize + 6MB)
    // = 31 MB at current configurations
    const val DEFAULT_UPLOAD_THREADS: Int = 2
    const val DEFAULT_QUEUE_CAPACITY: Int = 2
    const val DEFAULT_PART_SIZE_MB: Int = 5

    // MAX object size for AWS and GCS is 5TB (max allowed 10,000 parts*525mb)
    // (https://aws.amazon.com/s3/faqs/, https://cloud.google.com/storage/quotas)
    const val MAX_ALLOWED_PART_SIZE_MB: Int = 525
    const val DEFAULT_NUM_STREAMS: Int = 1

    @JvmStatic
    fun create(bucketName: String?, objectKey: String, s3Client: AmazonS3?): Builder {
        return Builder(bucketName, objectKey, s3Client)
    }

    class Builder
    internal constructor(
        private val bucketName: String?,
        private val objectKey: String,
        private val s3Client: AmazonS3?
    ) {
        private var userMetadata: Map<String, String>? = null
        private var partSize = DEFAULT_PART_SIZE_MB.toLong()

        fun setPartSize(partSize: Long): Builder {
            if (partSize < DEFAULT_PART_SIZE_MB) {
                logger.warn {
                    "Part size $partSize is smaller than the minimum allowed, default to $DEFAULT_PART_SIZE_MB"
                }
                this.partSize = DEFAULT_PART_SIZE_MB.toLong()
            } else if (partSize > MAX_ALLOWED_PART_SIZE_MB) {
                logger.warn {
                    "Part size $partSize is larger than the maximum allowed, default to $MAX_ALLOWED_PART_SIZE_MB"
                }
                this.partSize = MAX_ALLOWED_PART_SIZE_MB.toLong()
            } else {
                this.partSize = partSize
            }
            return this
        }

        fun setUserMetadata(userMetadata: Map<String, String>?): Builder {
            this.userMetadata = userMetadata
            return this
        }

        fun get(): StreamTransferManager {
            if (userMetadata == null) {
                userMetadata = emptyMap()
            }
            return StreamTransferManagerWithMetadata(
                    bucketName,
                    objectKey,
                    s3Client,
                    userMetadata,
                )
                .numStreams(DEFAULT_NUM_STREAMS)
                .queueCapacity(DEFAULT_QUEUE_CAPACITY)
                .numUploadThreads(DEFAULT_UPLOAD_THREADS)
                .partSize(partSize)
        }
    }
}
