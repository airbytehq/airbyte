/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStorageUploadConfiguration(
    val fileSizeBytes: Long = DEFAULT_FILE_SIZE_BYTES,
    val uploadPartSizeBytes: Long = DEFAULT_PART_SIZE_BYTES,
) {
    companion object {
        const val DEFAULT_PART_SIZE_BYTES: Long = 10 * 1024 * 1024 // File xfer is still using it
        const val DEFAULT_FILE_SIZE_BYTES: Long = 200 * 1024 * 1024
    }
}

interface ObjectStorageUploadConfigurationProvider {
    val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration
}
