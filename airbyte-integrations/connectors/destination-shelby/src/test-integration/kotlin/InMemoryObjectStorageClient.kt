import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import java.io.InputStream
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class InMemoryStreamingUpload<T : RemoteObject<*>>(
    private val remoteObject: T,
) : StreamingUpload<T> {
    override suspend fun uploadPart(part: ByteArray, index: Int) {
        // TODO track what's happening
    }

    override suspend fun complete(): T {
        return remoteObject
    }
}

class InMemoryObjectStorageClient<T : RemoteObject<*>> : ObjectStorageClient<T> {
    private val objects = ConcurrentHashMap<String, T>()

    override suspend fun list(prefix: String): Flow<T> = flow {
        objects.values.filter { it.key.startsWith(prefix) }.forEach { emit(it) }
    }

    override suspend fun move(key: String, toKey: String): T {
        val remoteObject = objects[key] ?: throw IllegalArgumentException("Object not found")
        return move(remoteObject, toKey)
    }

    override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
        TODO("Not yet implemented")
    }

    override suspend fun getMetadata(key: String): Map<String, String> {
        TODO("Not yet implemented")
    }

    override suspend fun put(key: String, bytes: ByteArray): T {
        TODO("Not yet implemented")
    }

    override suspend fun delete(key: String) {
        objects.remove(key)
    }

    override suspend fun startStreamingUpload(
        key: String,
        metadata: Map<String, String>
    ): StreamingUpload<T> {
        // TODO track what happens here
        return InMemoryStreamingUpload(objects[key] ?: throw IllegalArgumentException("Object $key not found"))
    }

    override suspend fun delete(remoteObject: T) {
        objects.remove(remoteObject.key)
    }

    override suspend fun move(remoteObject: T, toKey: String): T {
        val oldObject =
            objects.remove(remoteObject.key) ?: throw IllegalArgumentException("Object not found")
        objects[toKey] = remoteObject
        return remoteObject
    }
}
