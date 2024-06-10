/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.AirbyteMessage
import java.nio.file.Path
import java.util.*

/**
 * This interface provides a java interface over all interactions with a Destination from the POV of
 * the platform. It encapsulates the full lifecycle of the Destination as well as any inputs and
 * outputs.
 */
interface AirbyteDestination : CheckedConsumer<AirbyteMessage, Exception>, AutoCloseable {
    /**
     * Starts the Destination container. It instantiates a writer to write to STDIN on that
     * container. It also instantiates a reader to listen on STDOUT.
     *
     * @param destinationConfig
     * - contains the arguments that must be passed to the write method of the Destination.
     * @param jobRoot
     * - directory where the job can write data.
     * @param additionalEnvironmentVariables
     * @throws Exception
     * - throws if there is any failure in startup.
     */
    @Throws(Exception::class)
    fun start(
        destinationConfig: WorkerDestinationConfig,
        jobRoot: Path,
        additionalEnvironmentVariables: Map<String, String>
    )

    /**
     * Accepts an AirbyteMessage and writes it to STDIN of the Destination. Blocks if STDIN's buffer
     * is full.
     *
     * @param message message to send to destination.
     * @throws Exception
     * - throws if there is any failure in writing to Destination.
     */
    @Throws(Exception::class) override fun accept(message: AirbyteMessage)

    /**
     * This method is a flush to make sure all data that should be written to the Destination is
     * written. Any messages that have already been accepted ([AirbyteDestination.accept] ()}) will
     * be flushed. Any additional messages sent to accept will not be flushed. In fact, flush should
     * fail if the caller attempts to send it additional messages after calling this method.
     *
     * (Potentially should just rename it to flush)
     *
     * @throws Exception
     * - throws if there is any failure when flushing.
     */
    @Throws(Exception::class) fun notifyEndOfInput()

    /**
     * Means no more data will be emitted by the Destination. This may be because all data has
     * already been emitted or because the Destination container has exited.
     *
     * @return true, if no more data will be emitted. otherwise, false.
     */
    fun isFinished(): Boolean

    /**
     * Gets the exit value of the destination process. This should only be called after the
     * destination process has finished.
     *
     * @return exit code of the destination process
     * @throws IllegalStateException if the destination process has not exited
     */
    val exitValue: Int

    /**
     * Attempts to read an AirbyteMessage from the Destination.
     *
     * @return returns an AirbyteMessage if the Destination emits one. Otherwise, empty. This method
     * BLOCKS on waiting for the Destination to emit data to STDOUT.
     */
    fun attemptRead(): Optional<AirbyteMessage>

    /**
     * Attempts to shut down the Destination's container. Waits for a graceful shutdown, capped by a
     * timeout.
     *
     * @throws Exception
     * - throws if there is any failure in shutdown.
     */
    @Throws(Exception::class) override fun close()

    /**
     * Attempt to shut down the Destination's container quickly.
     *
     * @throws Exception
     * - throws if there is any failure in shutdown.
     */
    @Throws(Exception::class) fun cancel()
}
