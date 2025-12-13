/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf

/**
 * Exception thrown when a protobuf value type doesn't match the expected AirbyteType. This
 * indicates that the source connector is using the wrong protobuf setter method for the declared
 * schema type.
 */
class ProtobufTypeMismatchException(
    val streamName: String,
    val columnName: String,
    val expectedType: AirbyteType,
    val actualValueCase: AirbyteValueProtobuf.ValueCase,
) : RuntimeException(buildMessage(streamName, columnName, expectedType, actualValueCase)) {
    companion object {
        private fun buildMessage(
            streamName: String,
            columnName: String,
            expectedType: AirbyteType,
            actualValueCase: AirbyteValueProtobuf.ValueCase
        ): String {
            return """
                |Protobuf type mismatch detected in stream '$streamName', column '$columnName':
                |  Expected AirbyteType: $expectedType
                |  Actual protobuf ValueCase: $actualValueCase
                |This error indicates that the source connector is using the wrong protobuf setter method.
                |The source must use the protobuf setter that corresponds to the declared schema type.
                |Please fix the source connector to use the correct protobuf setter method for this column.
            """.trimMargin()
        }
    }
}
