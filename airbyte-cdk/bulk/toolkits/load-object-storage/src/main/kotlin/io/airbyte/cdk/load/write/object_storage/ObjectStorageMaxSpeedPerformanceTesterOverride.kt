/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.WriteOpOverride
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.random.Random
import kotlin.time.measureTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext

/**
 * Declare a singleton of this class to override the WriteOperation with a performance test that
 * will ignore the source and spam an object storage provider with garbage data from memory.
 *
 * The purpose is to allow you to test for max possible cloud performance given certain tuning
 * conditions.
 *
 * This assumes you're using [ObjectLoader] and are providing enough config to make it work.
 * Additionally, provide a singleton of [ObjectStorageMaxSpeedPerformanceTesterOverrideConfig].
 *
 * This reuses many of the [ObjectLoader] performance knobs, while also providing a matrix of
 * scenarios:
 *
 * [approach]:
 * - [Approach.ONE_OBJECT_PER_WORKER]: each worker feeds parts to exactly one object
 * - [Approach.DISTRIBUTED_PARTS]: parts are distributed evenly across workers w/o regard to object
 *
 * [completeAtEnd]: whether to complete as we go or at the end. In the distributed_parts approach,
 * this tests the impact of coordinating across threads on performance. For the
 * one_object_per_worker approach, this is effectively a test of how long completion takes when done
 * synchronously. (Really it's just for ensuring an apples-to-apples comparison between the two
 * approaches.)
 */
interface ObjectStorageMaxSpeedPerformanceTesterOverrideConfig {
    enum class Approach {
        ONE_OBJECT_PER_WORKER,
        DISTRIBUTED_PARTS
    }
    val approach: Approach
    val completeAtEnd: Boolean
}

class ObjectStorageMaxSpeedPerformanceTesterOverride(
    private val client: ObjectStorageClient<*>,
    private val catalog: DestinationCatalog,
    private val objectLoader: ObjectLoader,
    private val pathFactory: PathFactory,
    private val config: ObjectStorageMaxSpeedPerformanceTesterOverrideConfig
) : WriteOpOverride {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = SelfTerminating

    @OptIn(ExperimentalCoroutinesApi::class)
    override suspend fun execute() = coroutineScope {
        val prng = Random(System.currentTimeMillis())
        val randomPart = prng.nextBytes(objectLoader.partSizeBytes.toInt())
        val randomString = randomPart.take(32).joinToString("") { "%02x".format(it) }
        val stream = catalog.streams.first()
        val objectKey = pathFactory.getFinalDirectory(stream) + "/mock-perf-test-$randomString"

        val numParts = (objectLoader.objectSizeBytes / objectLoader.partSizeBytes).toInt()
        val partsPerWorker = numParts / objectLoader.numUploadWorkers
        val actualSizeBytes =
            partsPerWorker * objectLoader.numUploadWorkers * objectLoader.partSizeBytes

        log.info {
            "root key=$objectKey; part_size=${objectLoader.partSizeBytes}b; num_parts=$numParts (per_worker=$partsPerWorker); total_size=${actualSizeBytes}b; num_workers=${objectLoader.numUploadWorkers}"
        }

        val duration = measureTime {
            log.info { "Starting upload to $objectKey using approach ${config.approach}" }
            when (config.approach) {
                ObjectStorageMaxSpeedPerformanceTesterOverrideConfig.Approach
                    .ONE_OBJECT_PER_WORKER -> {
                    withContext(Dispatchers.IO.limitedParallelism(objectLoader.numUploadWorkers)) {
                        val uploads =
                            (0 until objectLoader.numUploadWorkers)
                                .map {
                                    async {
                                        val workerKey = "$objectKey-worker-$it"
                                        log.info { "Starting upload to $workerKey" }
                                        val upload = client.startStreamingUpload(workerKey)
                                        repeat(partsPerWorker) {
                                            log.info { "Uploading part ${it + 1} of $workerKey" }
                                            upload.uploadPart(randomPart, it + 1)
                                        }
                                        log.info { "Completing upload to $workerKey" }
                                        if (!config.completeAtEnd) {
                                            upload.complete()
                                        }
                                        Pair(workerKey, upload)
                                    }
                                }
                                .awaitAll()
                        if (config.completeAtEnd) {
                            uploads
                                .map { (key, upload) ->
                                    async {
                                        log.info { "Completing upload to $key" }
                                        upload.complete()
                                    }
                                }
                                .awaitAll()
                        }
                    }
                }
                ObjectStorageMaxSpeedPerformanceTesterOverrideConfig.Approach.DISTRIBUTED_PARTS -> {
                    withContext(Dispatchers.IO.limitedParallelism(objectLoader.numUploadWorkers)) {
                        val workerKeys =
                            (0 until objectLoader.numUploadWorkers).map { "$objectKey-worker-$it" }
                        val keysWithUploads =
                            workerKeys.map { Pair(it, client.startStreamingUpload(it)) }
                        val keysWithUploadsAndParts =
                            keysWithUploads
                                .flatMap { (key, upload) ->
                                    (0 until partsPerWorker).map { Triple(key, upload, it + 1) }
                                }
                                .shuffled()
                        val keyCounts =
                            ConcurrentHashMap(
                                workerKeys.associateWith { AtomicLong(partsPerWorker.toLong()) }
                            )
                        (0 until objectLoader.numUploadWorkers)
                            .map {
                                async {
                                    val range =
                                        keysWithUploadsAndParts.slice(
                                            it * partsPerWorker until (it + 1) * partsPerWorker
                                        )
                                    range.forEach { (key, upload, part) ->
                                        log.info { "[$it] Uploading part $part of $key" }
                                        upload.uploadPart(randomPart, part)
                                        if (!config.completeAtEnd) {
                                            if (keyCounts[key]!!.decrementAndGet() == 0L) {
                                                log.info { "[$it] Completing upload to $key" }
                                                upload.complete()
                                            }
                                        }
                                    }
                                }
                            }
                            .awaitAll()
                        if (config.completeAtEnd) {
                            keysWithUploads
                                .map { (key, upload) ->
                                    async {
                                        log.info { "Completing upload to $key" }
                                        upload.complete()
                                    }
                                }
                                .awaitAll()
                        }
                    }
                }
            }
        }
        val mbs = actualSizeBytes.toFloat() / duration.inWholeSeconds.toFloat() / 1024 / 1024
        log.info {
            // format mbs to 2 decimal places
            "Uploaded $actualSizeBytes bytes in $duration seconds (${"%.2f".format(mbs)} MB/s)"
        }
    }
}
