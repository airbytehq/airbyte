/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteProbeMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.mockk.every
import io.mockk.mockk
import io.mockk.verifySequence
import java.io.ByteArrayOutputStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ProtobufDataChannelReaderTest {
    val factory: DestinationMessageFactory = mockk(relaxed = true)

    @BeforeEach
    fun setup() {
        every { factory.fromAirbyteProtobufMessage(any(), any()) } returns mockk(relaxed = true)
    }

    private fun getRecord(index: Int) =
        AirbyteRecordMessageProtobuf.newBuilder()
            .setStreamNamespace("test_namespace")
            .setStreamName("test_stream")
            .setEmittedAtMs(100L)
            .addData(AirbyteValueProtobuf.newBuilder().setString("foo"))
            .addData(AirbyteValueProtobuf.newBuilder().setInteger(index.toLong()))
            .build()

    private fun getMessage(index: Int) =
        AirbyteMessageProtobuf.newBuilder().setRecord(getRecord(index)).build()

    @Test
    fun `protobuf reader reads correctly`() {
        val reader = ProtobufDataChannelReader(factory)
        val outputStream = ByteArrayOutputStream()
        repeat(10) { getMessage(it).writeDelimitedTo(outputStream) }
        outputStream.flush()
        val bytes = outputStream.toByteArray()
        val inputStream = bytes.inputStream()
        reader.read(inputStream).toList().also { Assertions.assertEquals(10, it.size) }
        verifySequence {
            (0 until 10).forEach { factory.fromAirbyteProtobufMessage(getMessage(it), any()) }
        }
    }

    @Test
    fun `empty heartbeat payload writes correctly`() {
        val reader = ProtobufDataChannelReader(factory)
        val outputStream = ByteArrayOutputStream()
        AirbyteMessageProtobuf.newBuilder()
            .setProbe(AirbyteProbeMessageProtobuf.newBuilder().build())
            .build()
            .writeDelimitedTo(outputStream)
        outputStream.flush()
        val bytes = outputStream.toByteArray()
        val inputStream = bytes.inputStream()
        reader.read(inputStream).toList().also { Assertions.assertEquals(1, it.size) }
    }
}
