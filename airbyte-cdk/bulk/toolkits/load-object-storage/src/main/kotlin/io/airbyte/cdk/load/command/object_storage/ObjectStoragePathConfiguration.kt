/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStoragePathConfiguration(
    val prefix: String,
    val stagingPrefix: String?,
    val pathSuffixPattern: String?,
    val fileNamePattern: String?
)

interface ObjectStoragePathConfigurationProvider {
    val objectStoragePathConfiguration: ObjectStoragePathConfiguration
}
