package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.WriteOpOverride
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
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
import org.apache.sshd.common.channel.StreamingChannel.Streaming

@Singleton
class S3V2WriteOpOverride(
    private val client: S3Client,
    private val catalog: DestinationCatalog,
    private val config: S3V2Configuration<*>,
    private val pathFactory: PathFactory,
): WriteOpOverride {
    private val log = KotlinLogging.logger { }

    override val terminalCondition: TerminalCondition = SelfTerminating

    @OptIn(ExperimentalCoroutinesApi::class)
    override suspend fun execute() = coroutineScope {
        val prng = Random(System.currentTimeMillis())
        val randomPart = prng.nextBytes(config.partSizeBytes.toInt())
        val randomString = randomPart.take(32).joinToString("") { "%02x".format(it) }
        val stream = catalog.streams.first()
        val objectKey = pathFactory.getFinalDirectory(stream) + "/mock-perf-test-$randomString"

        val numParts = (config.objectSizeBytes / config.partSizeBytes).toInt()
        val partsPerWorker = numParts / config.numUploadWorkers
        val actualSizeBytes = partsPerWorker * config.numUploadWorkers * config.partSizeBytes

        log.info {
            "root key=$objectKey; part_size=${config.partSizeBytes}b; num_parts=$numParts (per_worker=$partsPerWorker); total_size=${actualSizeBytes}b; num_workers=${config.numUploadWorkers}"
        }

        val duration = measureTime {
            log.info { "Starting upload to $objectKey using approach ${config.approach}" }
            if (config.approach == "one_object_per_worker") {
                withContext(Dispatchers.IO.limitedParallelism(config.numUploadWorkers)) {
                    val uploads = (0 until config.numUploadWorkers).map {
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
                    }.awaitAll()
                    if (config.completeAtEnd) {
                        uploads.map { (key, upload) ->
                            async {
                                log.info { "Completing upload to $key" }
                                upload.complete()
                            }
                        }.awaitAll()
                    }
                }
            } else if (config.approach == "distributed_parts") {
                withContext(Dispatchers.IO.limitedParallelism(config.numUploadWorkers)) {
                    val workerKeys = (0 until config.numUploadWorkers).map { "$objectKey-worker-$it" }
                    val keysWithUploads = workerKeys.map { Pair(it, client.startStreamingUpload(it)) }
                    val keysWithUploadsAndParts = keysWithUploads.flatMap { (key, upload) ->
                        (0 until partsPerWorker).map { Triple(key, upload, it + 1) }
                    }.shuffled()
                    val keyCounts = ConcurrentHashMap(workerKeys.associateWith { AtomicLong(partsPerWorker.toLong()) })
                        (0 until config.numUploadWorkers).map {
                            async {
                                val range =
                                    keysWithUploadsAndParts.slice(it * partsPerWorker until (it + 1) * partsPerWorker)
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
                        }.awaitAll()
                        if (config.completeAtEnd) {
                            keysWithUploads.map { (key, upload) ->
                                async {
                                    log.info { "Completing upload to $key" }
                                    upload.complete()
                                }
                            }.awaitAll()
                        }
                    }
            } else {
                error("Unknown approach: ${config.approach}")
            }
        }
        val mbs = actualSizeBytes.toFloat() / duration.inWholeSeconds.toFloat() / 1024 / 1024
        log.info {
            // format mbs to 2 decimal places
            "Uploaded $actualSizeBytes bytes in $duration seconds (${"%.2f".format(mbs)} MB/s)"
        }
    }
}
