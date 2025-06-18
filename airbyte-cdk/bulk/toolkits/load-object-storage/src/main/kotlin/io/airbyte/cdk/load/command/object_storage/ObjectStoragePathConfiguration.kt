/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

data class ObjectStoragePathConfiguration(
    val prefix: String,
    val pathPattern: String?,
    val fileNamePattern: String?,
    val resolveNamesMethod: ((String) -> String)? = null
)

interface ObjectStoragePathConfigurationProvider {
    val objectStoragePathConfiguration: ObjectStoragePathConfiguration
}
