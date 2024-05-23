/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import java.util.concurrent.Executors
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.atomic.AtomicInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DebeziumShutdownProcedureTest {
    @Test
    @Throws(InterruptedException::class)
    fun test() {
        val sourceQueue = LinkedBlockingQueue<Int>(10)
        val recordsInserted = AtomicInteger()
        val executorService = Executors.newSingleThreadExecutor()
        val debeziumShutdownProcedure =
            DebeziumShutdownProcedure(
                sourceQueue,
                { executorService.shutdown() },
                { recordsInserted.get() >= 99 }
            )
        executorService.execute {
            for (i in 0..99) {
                try {
                    sourceQueue.put(i)
                    recordsInserted.set(i)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
            }
        }

        Thread.sleep(1000)
        debeziumShutdownProcedure.initiateShutdownProcedure()

        Assertions.assertEquals(99, recordsInserted.get())
        Assertions.assertEquals(0, sourceQueue.size)
        Assertions.assertEquals(100, debeziumShutdownProcedure.recordsRemainingAfterShutdown.size)

        for (i in 0..99) {
            Assertions.assertEquals(
                i,
                debeziumShutdownProcedure.recordsRemainingAfterShutdown.poll()
            )
        }
    }
}
