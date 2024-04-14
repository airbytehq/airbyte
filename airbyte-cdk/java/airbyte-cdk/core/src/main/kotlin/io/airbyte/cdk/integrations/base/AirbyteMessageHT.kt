package io.airbyte.cdk.integrations.base

import io.airbyte.protocol.models.v0.AirbyteMessage

class AirbyteMessageHT(var recordHT: Any) : AirbyteMessage() {
    override fun toString(): String {
        return "{\"type\":\"RECORD\",\"record\":$recordHT}"
    }
}
