/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.AirbyteMessage
import java.nio.file.Path
import java.util.*

/**
 * This interface provides a java interface over all interactions with a Source from the POV of the
 * platform. It encapsulates the full lifecycle of the Source as well as any outputs.
 */
interface AirbyteSource : AutoCloseable {
    /**
     * Starts the Source container and opens a connection to STDOUT on that container.
     *
     * @param sourceConfig
     * - contains the arguments that must be passed to the read method of the Source.
     * @param jobRoot
     * - directory where the job can write data.
     * @throws Exception
     * - throws if there is any failure in startup.
     */
    @Throws(Exception::class) fun start(sourceConfig: WorkerSourceConfig, jobRoot: Path)

    /**
     * Means no more data will be emitted by the Source. This may be because all data has already
     * been emitted or because the Source container has exited.
     *
     * @return true, if no more data will be emitted. otherwise, false.
     */
    val isFinished: Boolean

    /**
     * Gets the exit value of the source process. This should only be called after the source
     * process has finished.
     *
     * @return exit code of the source process
     * @throws IllegalStateException if the source process has not exited
     */
    val exitValue: Int

    /**
     * Attempts to read an AirbyteMessage from the Source.
     *
     * @return returns an AirbyteMessage is the Source emits one. Otherwise, empty. This method
     * BLOCKS on waiting for the Source to emit data to STDOUT.
     */
    fun attemptRead(): Optional<AirbyteMessage>

    /**
     * Attempts to shut down the Source's container. Waits for a graceful shutdown, capped by a
     * timeout.
     *
     * @throws Exception
     * - throws if there is any failure in shutdown.
     */
    @Throws(Exception::class) override fun close()

    /**
     * Attempt to shut down the Source's container quickly.
     *
     * @throws Exception
     * - throws if there is any failure in shutdown.
     */
    @Throws(Exception::class) fun cancel()
}
