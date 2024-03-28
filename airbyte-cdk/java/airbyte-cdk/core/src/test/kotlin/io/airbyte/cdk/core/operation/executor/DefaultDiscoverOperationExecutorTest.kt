/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.protocol.models.v0.AirbyteMessage
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultDiscoverOperationExecutorTest {
    @Test
    @SuppressFBWarnings(
        value = ["RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE"],
        justification = "Invalid warning for Kotlin",
    )
    internal fun testThatTheExpectedAirbyteMessageIsReturnedWhenExecuted() {
        val executor = DefaultDiscoverOperationExecutor()
        val result = executor.execute()
        assertTrue(result.isSuccess)
        result.onSuccess {
            assertEquals(AirbyteMessage.Type.CATALOG, it?.type)
            assertNotNull(it?.catalog)
        }
    }
}
