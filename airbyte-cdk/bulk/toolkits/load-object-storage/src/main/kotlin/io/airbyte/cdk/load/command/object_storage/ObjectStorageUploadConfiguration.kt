/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStorageUploadConfiguration(val streamingUploadPartSize: Long)

interface ObjectStorageUploadConfigurationProvider {
    val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration
}
