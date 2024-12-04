/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStorageUploadConfiguration(
    val streamingUploadPartSize: Long = DEFAULT_STREAMING_UPLOAD_PART_SIZE,
    val maxNumConcurrentUploads: Int = DEFAULT_MAX_NUM_CONCURRENT_UPLOADS
) {
    companion object {
        const val DEFAULT_STREAMING_UPLOAD_PART_SIZE = 5L * 1024L * 1024L
        const val DEFAULT_MAX_NUM_CONCURRENT_UPLOADS = 2
    }
}

interface ObjectStorageUploadConfigurationProvider {
    val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration
}
