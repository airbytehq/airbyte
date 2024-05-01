/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test suite for the [StateGeneratorUtils] class. */
class StateGeneratorUtilsTest {
    @Test
    fun testValidStreamDescriptor() {
        val streamDescriptor1: StreamDescriptor? = null
        val streamDescriptor2 = StreamDescriptor()
        val streamDescriptor3 = StreamDescriptor().withName("name")
        val streamDescriptor4 = StreamDescriptor().withNamespace("namespace")
        val streamDescriptor5 = StreamDescriptor().withName("name").withNamespace("namespace")
        val streamDescriptor6 = StreamDescriptor().withName("name").withNamespace("")
        val streamDescriptor7 = StreamDescriptor().withName("").withNamespace("namespace")
        val streamDescriptor8 = StreamDescriptor().withName("").withNamespace("")

        Assertions.assertFalse(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor1))
        Assertions.assertFalse(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor2))
        Assertions.assertTrue(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor3))
        Assertions.assertFalse(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor4))
        Assertions.assertTrue(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor5))
        Assertions.assertTrue(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor6))
        Assertions.assertTrue(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor7))
        Assertions.assertTrue(StateGeneratorUtils.isValidStreamDescriptor(streamDescriptor8))
    }
}
