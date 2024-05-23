/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import com.google.common.annotations.VisibleForTesting
import java.util.stream.Stream
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Registers a shutdown hook that calls the close method of the provided objects. If an object does
 * not support either the [AutoCloseable] or [Closeable] interface, it will be ignored.
 *
 * This is a temporary class that is being provided to ensure that resources created by each
 * application are properly closed on shutdown. This logic will no longer be necessary once an
 * application framework is introduced to the project that can provide object lifecycle management.
 */
object CloseableShutdownHook {
    private val log: Logger = LoggerFactory.getLogger(CloseableShutdownHook::class.java)

    /**
     * Registers a runtime shutdown hook with the application for each provided closeable object.
     *
     * @param objects An array of objects to be closed on application shutdown.
     */
    fun registerRuntimeShutdownHook(vararg objects: Any) {
        Runtime.getRuntime().addShutdownHook(buildShutdownHookThread(*objects))
    }

    /**
     * Builds the [Thread] that will be registered as an application shutdown hook.
     *
     * @param objects An array of objects to be closed on application shutdown.
     * @return The application shutdown hook [Thread].
     */
    @VisibleForTesting
    fun buildShutdownHookThread(vararg objects: Any): Thread {
        val autoCloseables: Collection<AutoCloseable> =
            Stream.of(*objects)
                .filter { o: Any -> o is AutoCloseable }
                .map { obj: Any -> AutoCloseable::class.java.cast(obj) }
                .toList()

        return Thread { autoCloseables.forEach { it.close() } }
    }

    private fun close(autoCloseable: AutoCloseable) {
        try {
            autoCloseable.close()
        } catch (e: Exception) {
            log.error("Unable to close object {}.", autoCloseable.javaClass.name, e)
        }
    }
}
