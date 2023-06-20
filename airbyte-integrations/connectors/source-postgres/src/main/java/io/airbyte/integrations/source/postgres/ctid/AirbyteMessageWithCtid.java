package io.airbyte.integrations.source.postgres.ctid;

import io.airbyte.protocol.models.v0.AirbyteMessage;

public record AirbyteMessageWithCtid(AirbyteMessage recordMessage, String ctid) {

}
