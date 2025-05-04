/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test

import io.airbyte.integrations.source.e2e_test.JavaSocketWriter.Companion.RECORD
import io.airbyte.integrations.source.e2e_test.JavaSocketWriter.Companion.RECORD2
import java.util.concurrent.CompletableFuture.runAsync

class JavaStandardOutWriter {

    fun write() {
        val listOf =
            listOf(
                runAsync { writeFromOneThread() },
                runAsync { writeFromOneThread2() },
            )
        listOf.forEach { it.join() }
    }

    private fun writeFromOneThread() {
        DummyIterator().use { it.forEachRemaining { System.out.println(RECORD) } }
    }

    private fun writeFromOneThread2() {
        DummyIterator().use { it.forEachRemaining { System.out.println(RECORD2) } }
    }
}
