package io.airbyte.cdk.integrations.destination_async.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import io.airbyte.cdk.integrations.destination_async.dto.AirbyteMessage.AirbyteRecordMessageWrapper;
import io.airbyte.cdk.integrations.destination_async.dto.AirbyteMessage.AirbyteStateMessageWrapper;
import lombok.Getter;
import lombok.Setter;

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.EXISTING_PROPERTY, property = "type", visible = true)
@JsonSubTypes({
    @JsonSubTypes.Type(value = AirbyteRecordMessageWrapper.class, name = "RECORD"),
    @JsonSubTypes.Type(value = AirbyteStateMessageWrapper.class, name = "STATE")
})
public class AirbyteMessage {

  @JsonProperty("type")
  io.airbyte.protocol.models.v0.AirbyteMessage.Type type;

  public AirbyteMessage() {}

  @Setter
  @Getter
  public static class AirbyteRecordMessageWrapper extends AirbyteMessage {
    @JsonProperty("record")
    private AirbyteRecordMessage record;

    public AirbyteRecordMessageWrapper() {}

  }

  @Setter
  @Getter
  public static class AirbyteStateMessageWrapper extends AirbyteMessage {
    @JsonProperty("state")
    private AirbyteStateMessage state;

    public AirbyteStateMessageWrapper() {}

  }

}
