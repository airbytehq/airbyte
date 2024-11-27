/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.flow.flow

class MockRemoteObject(
    override val key: String,
    override val storageConfig: Int,
    val data: ByteArray,
    val metadata: Map<String, String> = emptyMap()
) : RemoteObject<Int>

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
@Singleton
@Requires(env = ["MockObjectStorageClient"])
class MockObjectStorageClient : ObjectStorageClient<MockRemoteObject> {
    private val objects = ConcurrentHashMap<String, MockRemoteObject>()

    override suspend fun list(prefix: String) = flow {
        objects.values.filter { it.key.startsWith(prefix) }.forEach { emit(it) }
    }

    override suspend fun move(remoteObject: MockRemoteObject, toKey: String): MockRemoteObject {
        val oldObject =
            objects.remove(remoteObject.key) ?: throw IllegalArgumentException("Object not found")
        val newObject = MockRemoteObject(toKey, oldObject.storageConfig, oldObject.data)
        objects[toKey] = newObject
        return newObject
    }

    override suspend fun move(key: String, toKey: String): MockRemoteObject {
        val remoteObject = objects[key] ?: throw IllegalArgumentException("Object not found")
        return move(remoteObject, toKey)
    }

    override suspend fun <R> get(key: String, block: (InputStream) -> R): R {
        val remoteObject = objects[key] ?: throw IllegalArgumentException("Object not found")
        return block(remoteObject.data.inputStream())
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        return objects[key]?.metadata ?: emptyMap()
    }

    override suspend fun put(key: String, bytes: ByteArray): MockRemoteObject {
        val remoteObject = MockRemoteObject(key, 0, bytes)
        objects[key] = remoteObject
        return remoteObject
    }

    override suspend fun delete(key: String) {
        objects.remove(key)
    }

    override suspend fun <V : OutputStream> streamingUpload(
        key: String,
        metadata: Map<String, String>,
        streamProcessor: StreamProcessor<V>?,
        block: suspend (OutputStream) -> Unit
    ): MockRemoteObject {
        val outputStream = ByteArrayOutputStream()
        block(outputStream)
        val remoteObject = MockRemoteObject(key, 0, outputStream.toByteArray(), metadata)
        objects[key] = remoteObject
        return remoteObject
    }

    override suspend fun delete(remoteObject: MockRemoteObject) {
        objects.remove(remoteObject.key)
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<MockRemoteObject> {
        TODO("Not yet implemented")
    }
}
