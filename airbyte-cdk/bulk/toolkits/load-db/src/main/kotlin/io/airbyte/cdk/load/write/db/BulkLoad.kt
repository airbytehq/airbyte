/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.write.object_storage.ObjectLoader

/**
 * [BulkLoad] is for the use case in which a destination first stages records in a temporary
 * location, usually cloud object storage, then loads them into the destination database in bulk.
 *
 * To use, declare a singleton of type [BulkLoadFactory] and implement the [BulkLoadFactory.create]
 * method.
 *
 * This strategy composes [ObjectLoader] with a post-processing step provided by the [load] method.
 * As [ObjectLoader] makes loaded objects as they become available, [load] is called on each one in
 * sequence.
 *
 * [BulkLoadFactory.maxNumConcurrentLoads] determines the number of concurrent loads that can be in
 * progress at once.
 *
 * The key type [K] determines how the destination will partition the work. By default,
 * [io.airbyte.cdk.load.message.StreamKey] is provided and an interface using this type will just
 * work. Specifically, no more than one [load] will ever be in progress per stream, but up to
 * [BulkLoadFactory.maxNumConcurrentLoads] can be in progress at once.
 *
 * Additionally, the configuration values provided by [ObjectLoader] can be overridden on the
 * factory and will work as documents.
 *
 * The factory method [BulkLoadFactory.create] will be called once per key the first time a key is
 * seen. It is guaranteed to be closed if created.
 *
 * To adjust this behavior, declare a named singleton "objectLoaderOutputPartitioner" using the
 * desired key and/or partition strategy. (See
 * [io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadStep])
 *
 * TODO: provide a method that allows the user to check for an available connection and defer work
 * if it is not available.
 */
interface BulkLoad<K : WithStream, T : RemoteObject<*>> : AutoCloseable {
    /** Called as uploaded parts become available */
    suspend fun load(remoteObject: T)
}

interface BulkLoadFactory<K : WithStream, T : RemoteObject<*>> : ObjectLoader {
    val maxNumConcurrentLoads: Int
    override val batchStateOnUpload: Batch.State
        get() = Batch.State.PERSISTED

    fun create(key: K): BulkLoad<K, T>
}
