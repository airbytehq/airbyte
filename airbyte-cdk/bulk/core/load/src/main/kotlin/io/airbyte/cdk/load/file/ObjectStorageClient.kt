/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.message.RemoteObject

interface ObjectStorageClient<T : RemoteObject> {
    suspend fun list(prefix: String): List<T>
}
