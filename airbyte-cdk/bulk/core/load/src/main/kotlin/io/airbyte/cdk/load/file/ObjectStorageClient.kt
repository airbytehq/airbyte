/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.message.RemoteObject
import java.nio.file.Path

interface ObjectStorageClient<T : RemoteObject> {
    suspend fun list(prefix: Path): List<T>
}
