/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStorageUploadConfiguration(
    val streamingUploadPartSize: Long = DEFAULT_STREAMING_UPLOAD_PART_SIZE,
) {
    companion object {
        const val DEFAULT_STREAMING_UPLOAD_PART_SIZE = 5L * 1024L * 1024L
    }
}

interface ObjectStorageUploadConfigurationProvider {
    val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration
}
