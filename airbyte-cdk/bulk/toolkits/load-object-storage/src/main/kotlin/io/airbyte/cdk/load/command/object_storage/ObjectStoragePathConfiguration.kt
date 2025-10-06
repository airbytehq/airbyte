/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.object_storage

import io.airbyte.cdk.load.data.Transformations

data class ObjectStoragePathConfiguration(
    val prefix: String,
    val pathPattern: String?,
    val fileNamePattern: String?,
    val resolveNamesMethod: ((String) -> String) = { Transformations.toS3SafeCharacters(it) }
)

interface ObjectStoragePathConfigurationProvider {
    val objectStoragePathConfiguration: ObjectStoragePathConfiguration
}
