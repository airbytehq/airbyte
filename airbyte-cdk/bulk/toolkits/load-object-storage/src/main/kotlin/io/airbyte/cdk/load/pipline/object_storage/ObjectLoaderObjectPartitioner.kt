/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlin.math.abs
import kotlin.random.Random

/**
 * The default output partitioner for the ObjectLoader pipeline. It will not actually be used unless
 * an output queue for the loaded objects is provided. (see
 * [io.airbyte.cdk.load.write.object_storage.ObjectLoader]).
 *
 * In that case, the default behavior will be to key and partition by stream. This means that the
 * number of concurrent loaders can be chosen based on the available resources, but no individual
 * stream will ever run concurrently.
 */
@Singleton
@Secondary
@Requires(bean = ObjectLoader::class)
@Named("objectLoaderOutputPartitioner")
class ObjectLoaderObjectPartitioner<T : RemoteObject<*>> :
    OutputPartitioner<
        ObjectKey,
        Part,
        StreamKey,
        LoadedObject<T>,
    > {
    // TODO: Abstract this out to a round-robin partition generator
    private var nextPartition = Random(System.currentTimeMillis()).nextInt(Int.MAX_VALUE)

    override fun getPart(outputKey: StreamKey, numParts: Int): Int {
        val part = nextPartition++
        return if (part == Int.MIN_VALUE) {
            0
        } else {
            abs(part) % numParts
        }
    }

    override fun getOutputKey(inputKey: ObjectKey, output: LoadedObject<T>): StreamKey =
        StreamKey(inputKey.stream)
}
