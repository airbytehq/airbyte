/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.valueForProtobufEncoding
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.integrations.source.postgres.operations.types.PostgresMoneyFieldType
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class PostgresMoneyFieldTypeTest {

    private val protobufEncoder = AirbyteValueProtobufEncoder()

    @Test
    fun `encodes scalar money for protobuf while preserving JSON strings`() {
        val jsonEncoder = PostgresMoneyFieldType.jsonEncoder as JsonEncoder<in String>

        listOf("999.99", "-1000.0", "0.0").forEach { value ->
            val fieldValueEncoder = FieldValueEncoder(value, jsonEncoder)
            val protobufValue =
                protobufEncoder
                    .encode(
                        valueForProtobufEncoding(fieldValueEncoder),
                        LeafAirbyteSchemaType.NUMBER
                    )
                    .build()

            assertEquals(AirbyteValueProtobuf.ValueCase.BIG_DECIMAL, protobufValue.valueCase)
            assertEquals(BigDecimal(value).toPlainString(), protobufValue.bigDecimal)
            assertEquals(TextNode(value), PostgresMoneyFieldType.jsonEncoder.encode(value))
        }
    }
}
