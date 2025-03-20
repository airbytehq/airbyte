/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.write.object_storage.ObjectLoader

/**
 * [BulkLoader] is for the use case in which a destination first stages records in a temporary
 * location, usually cloud object storage, then loads them into the destination database in bulk.
 *
 * To use, declare a singleton of type [BulkLoaderFactory] and implement the
 * [BulkLoaderFactory.create] method.
 *
 * This strategy composes [ObjectLoader] with a post-processing step provided by the [load] method.
 * As [ObjectLoader] makes loaded objects available, [load] is called on each one in sequence.
 *
 * [BulkLoaderFactory.maxNumConcurrentLoads] determines the number of concurrent loads that can be
 * in progress at once.
 *
 * The key type [K] determines how the destination will partition the work. By default,
 * [io.airbyte.cdk.load.message.StreamKey] is provided and an interface using this type will just
 * work. Specifically, no more than one [load] will ever be in progress per stream, but up to
 * [BulkLoaderFactory.maxNumConcurrentLoads] can be in progress at once.
 *
 * Additionally, the configuration values provided by [ObjectLoader] can be overridden on the
 * factory and will work as documents.
 *
 * The factory method [BulkLoaderFactory.create] will be called once per key the first time a key is
 * seen. It is guaranteed to be closed if created.
 *
 * To adjust this behavior, declare a named singleton "objectLoaderOutputPartitioner" using the
 * desired key and/or partition strategy. (See
 * [io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleterStep])
 *
 * TODO: provide a method that allows the user to check for an available connection and defer work
 * if it is not available.
 */
interface BulkLoader<T> : AutoCloseable {
    suspend fun load(remoteObject: T)
}

interface BulkLoaderFactory<K : WithStream, T : RemoteObject<*>> : ObjectLoader {
    val maxNumConcurrentLoads: Int

    fun create(key: K, partition: Int): BulkLoader<T>

    // Override the bookkeeping state for objects in object storage
    // from the default of "COMPLETE". Connector devs can ignore this.
    override val stateAfterUpload: Batch.State
        get() = Batch.State.LOADED
}
