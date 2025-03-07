/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedReader
import java.io.InputStream
import java.time.Clock
import java.time.Instant
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlin.io.path.Path
import kotlin.io.path.createTempFile
import kotlin.io.path.fileSize
import kotlin.io.path.getLastModifiedTime
import kotlin.io.path.pathString
import kotlin.text.Charsets.UTF_8
import kotlin.time.measureTime
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.future.await

/** Base class for JDBC implementations of [PartitionReader]. */
sealed class JdbcPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
) : PartitionReader {

    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier
    val streamRecordConsumer: StreamRecordConsumer =
        streamState.streamFeedBootstrap.streamRecordConsumer()

    private val acquiredResources = AtomicReference<AcquiredResources>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            partition.tryAcquireResourcesForReader()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(row: SelectQuerier.ResultRow) {
        streamRecordConsumer.accept(row.data, row.changes)
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }

    /** If configured max feed read time elapsed we exit with a transient error */
    protected fun checkMaxReadTimeElapsed() {
        sharedState.configuration.maxSnapshotReadDuration?.let {
            if (java.time.Duration.between(sharedState.snapshotReadStartTime, Instant.now()) > it) {
                throw TransientErrorException("Shutting down snapshot reader: max duration elapsed")
            }
        }
    }
}

/** JDBC implementation of [PartitionReader] which reads the [partition] in its entirety. */
class JdbcNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {
    private val log = KotlinLogging.logger {}

    fun commands(query: String): List<String> = listOf(
        "mysql",
        "--quick",
        "--raw",
        "-ss",
        "-P",
        sharedState.configuration.realPort.toString(),
        "-h",
        sharedState.configuration.realHost,
        "-u",
        sharedState.configuration.jdbcProperties.get("user")!!,
        "-p${sharedState.configuration.jdbcProperties.get("password")}",
        "-e$query"
    )

    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
        /* Don't start read if we've gone over max duration.
        We check for elapsed duration before reading and not while because
        existing exiting with an exception skips checkpoint(), so any work we
        did before time has elapsed will be wasted. */
        checkMaxReadTimeElapsed()

        fun collectOutput(inputStream: InputStream): String {
            val out = StringBuilder()
            val buf: BufferedReader = inputStream.bufferedReader(UTF_8)
            var line: String? = buf.readLine()
            do {
                if (line != null) {
                    out.append(line).append("\n")
                }
                line = buf.readLine()
            } while (line != null)
            return out.toString()
        }
        /////////////////////////////////
        // form query
        var q = partition.nonResumableQuery.sql
        val bindings = partition.nonResumableQuery.bindings
        for (binding in bindings) {
            q = q.replaceFirst("?", binding.value.toString())
        }

        // Run mysql
        val cmds = commands(q)

        val pb = ProcessBuilder(cmds)
        val file = createTempFile(Path("/tmp"), "ab", ".txt")
        pb.redirectOutput(file.toFile())

        log.info { "Running $cmds to ${file}" }
        val timeTaken = measureTime {
            val process = pb.start()
            val finishedP = process.onExit().await()
            if (finishedP.exitValue() != 0) {
                log.error { "Failed to execute command: ${pb.command()}" }
                log.error { collectOutput(process.errorStream) }
                throw RuntimeException()
            }
        }

        log.info { "${file} Time taken: $timeTaken" }
        // emit record + file_url
        val recordTemplate =
            "{\"type\":\"RECORD\",\"record\":{\"stream\":\"${stream.namespace}.${stream.name}\",\"file\":{\"file_url\":\"${file.pathString}\",\"bytes\":${file.fileSize()},\"file_relative_path\":\"${file.fileName}\",\"modified\":${file.getLastModifiedTime().toMillis()},\"source_file_url\":\"${file.fileName}\"},\"emitted_at\":${Clock.systemUTC().millis()},\"data\":{}}}"
        println(recordTemplate)
        /////////////////////////////////

        /*selectQuerier
            .executeQuery(
                q = partition.nonResumableQuery,
                parameters =
                    SelectQuerier.Parameters(
                        reuseResultObject = true,
                        fetchSize = streamState.fetchSize
                    ),
            )
            .use { result: SelectQuerier.Result ->
                for (row in result) {
                    out(row)
                    numRecords.incrementAndGet()
                }
            }*/
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        // Sanity check.
        if (!runComplete.get()) throw RuntimeException("cannot checkpoint non-resumable read")
        // The run method executed to completion without a LIMIT clause.
        // This implies that the partition boundary has been reached.
        return PartitionReadCheckpoint(partition.completeState, numRecords.get())
    }
}

/**
 * JDBC implementation of [PartitionReader] which reads as much as possible of the [partition], in
 * order, before timing out.
 */
class JdbcResumablePartitionReader<P : JdbcSplittablePartition<*>>(
    partition: P,
) : JdbcPartitionReader<P>(partition) {

    val incumbentLimit = AtomicLong()
    val numRecords = AtomicLong()
    val lastRecord = AtomicReference<ObjectNode?>(null)
    val runComplete = AtomicBoolean(false)

    override suspend fun run() {
        /* Don't start read if we've gone over max duration.
        We check for elapsed duration before reading and not while because
        existing exiting with an exception skips checkpoint(), so any work we
        did before time has elapsed will be wasted. */
        checkMaxReadTimeElapsed()

        val fetchSize: Int = streamState.fetchSizeOrDefault
        val limit: Long = streamState.limit
        incumbentLimit.set(limit)
        selectQuerier
            .executeQuery(
                q = partition.resumableQuery(limit),
                parameters =
                    SelectQuerier.Parameters(reuseResultObject = true, fetchSize = fetchSize),
            )
            .use { result: SelectQuerier.Result ->
                for (row in result) {
                    out(row)
                    lastRecord.set(row.data)
                    // Check activity periodically to handle timeout.
                    if (numRecords.incrementAndGet() % fetchSize == 0L) {
                        coroutineContext.ensureActive()
                    }
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        if (runComplete.get() && numRecords.get() < streamState.limit) {
            // The run method executed to completion with a LIMIT clause which was not reached.
            return PartitionReadCheckpoint(partition.completeState, numRecords.get())
        }
        // The run method ended because of either the LIMIT or the timeout.
        // Adjust the LIMIT value so that it grows or shrinks to try to fit the timeout.
        if (incumbentLimit.get() > 0L) {
            if (runComplete.get() && streamState.limit <= incumbentLimit.get()) {
                // Increase the limit clause for the next PartitionReader, because it's too small.
                // If it had been bigger then run might have executed for longer.
                streamState.updateLimitState { it.up }
            }
            if (!runComplete.get() && incumbentLimit.get() <= streamState.limit) {
                // Decrease the limit clause for the next PartitionReader, because it's too big.
                // If it had been smaller then run might have completed in time.
                streamState.updateLimitState { it.down }
            }
        }
        val checkpointState: OpaqueStateValue = partition.incompleteState(lastRecord.get()!!)
        return PartitionReadCheckpoint(checkpointState, numRecords.get())
    }
}
