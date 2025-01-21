package io.airbyte.cdk.load.file.object_storage

import kotlinx.coroutines.flow.Flow

/**
 * Just for testing old CDK in default open task.
 */
interface StateObjectStorageLite<T> {
    fun list(prefix: String): Flow<T>
    fun getMetadata(key: String): Map<String, String>
}
