package io.airbyte.cdk.integrations.destination_async.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteStreamState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class AirbyteStateMessage {

  @JsonProperty("type")
  private AirbyteStateType type;

  @JsonProperty("stream")
  private PartialAirbyteStreamState stream;

}
