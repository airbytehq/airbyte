package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.WriteOpOverride
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.random.Random
import kotlin.time.measureTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext

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
            withContext(Dispatchers.IO.limitedParallelism(config.numUploadWorkers)) {
                (0 until config.numUploadWorkers).map {
                    async {
                        val workerKey = "$objectKey-worker-$it"
                        log.info { "Starting upload to $workerKey" }
                        val upload = client.startStreamingUpload(workerKey)
                        repeat(partsPerWorker) {
                            log.info { "Uploading part ${it + 1} of $workerKey" }
                            upload.uploadPart(randomPart, it + 1)
                        }
                        log.info { "Completing upload to $workerKey" }
                        upload.complete()
                    }
                }.awaitAll()
            }
        }
        val mbs = actualSizeBytes.toFloat() / duration.inWholeSeconds.toFloat() / 1024 / 1024
        log.info {
            // format mbs to 2 decimal places
            "Uploaded $actualSizeBytes bytes in $duration seconds (${"%.2f".format(mbs)} MB/s)"
        }
    }
}
