/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext

class ObjectStorageDestinationCleaner<T : RemoteObject<*>> {
    fun cleanup(
        stream: DestinationStream,
        client: ObjectStorageClient<T>,
        pathFactory: ObjectStoragePathFactory,
    ) {
        val prefix = pathFactory.getFinalDirectory(stream).toString()
        runBlocking {
            withContext(Dispatchers.IO) { client.list(prefix).collect { client.delete(it) } }
        }
    }
}
