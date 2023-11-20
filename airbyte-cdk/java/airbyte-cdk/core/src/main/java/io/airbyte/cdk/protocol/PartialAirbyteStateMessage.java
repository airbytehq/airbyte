package io.airbyte.cdk.protocol;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Map;
import java.util.Objects;

public class PartialAirbyteStateMessage {

  AirbyteStateMessage.AirbyteStateType type;
  PartialAirbyteStreamState stream;
  private PartialAirbyteGlobalState global;
  // deprecated legacy state blob
  String serializedData;

  public static PartialAirbyteStateMessage fromJson(final StringIterator message) {
    final PartialAirbyteStateMessage state = new PartialAirbyteStateMessage();
    final boolean nonNull = PartialJsonDeserializer.processObject(
        message,
        Map.of(
            "type", (typeIterator) -> state.type = AirbyteStateMessage.AirbyteStateType.valueOf(PartialJsonDeserializer.readStringValue(typeIterator)),
            "stream", (streamIterator) -> state.stream = PartialAirbyteStreamState.fromJson(streamIterator),
            "data", (dataIterator) -> state.serializedData = PartialJsonDeserializer.readSerializedValue(dataIterator)
        )
    );
    if (nonNull) {
      return state;
    } else {
      return null;
    }
  }

  public AirbyteStateMessage.AirbyteStateType getType() {
    return type;
  }

  public PartialAirbyteStreamState getStream() {
    return stream;
  }

  public String serialize() {
    String output = "{";
    output += "\"type\": \"" + type + "\"";
    if (stream != null) {
      output += ", \"stream\": " + stream.serialize();
    }
    output += "}";
    return output;
  }

  @Override
  public String toString() {
    return "PartialAirbyteStateMessage{" +
        "type=" + type +
        ", stream=" + stream +
        ", global=" + global +
        ", serializedData='" + serializedData + '\'' +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;

    final PartialAirbyteStateMessage that = (PartialAirbyteStateMessage) o;

    if (type != that.type) return false;
    if (!Objects.equals(stream, that.stream)) return false;
    if (!Objects.equals(global, that.global)) return false;
    return Objects.equals(serializedData, that.serializedData);
  }

  @Override
  public int hashCode() {
    int result = type != null ? type.hashCode() : 0;
    result = 31 * result + (stream != null ? stream.hashCode() : 0);
    result = 31 * result + (global != null ? global.hashCode() : 0);
    result = 31 * result + (serializedData != null ? serializedData.hashCode() : 0);
    return result;
  }

  public AirbyteStateMessage toFullStateMessage() {
    final AirbyteStateMessage stateMessage = new AirbyteStateMessage();
    stateMessage.setType(type);
    if (stream != null) {
      stateMessage.setStream(stream.toFullStreamState());
    }
    if (global != null) {
      stateMessage.setGlobal(global.toFullGlobalState());
    }
    if (serializedData != null) {
      stateMessage.setData(Jsons.deserialize(serializedData));
    }
    return stateMessage;
  }

  public PartialAirbyteStateMessage withType(final AirbyteStateMessage.AirbyteStateType type) {
    this.type = type;
    return this;
  }

  public PartialAirbyteStateMessage withStream(final PartialAirbyteStreamState stream) {
    this.stream = stream;
    return this;
  }

  public PartialAirbyteStateMessage withGlobal(final PartialAirbyteGlobalState global) {
    this.global = global;
    return this;
  }

  public PartialAirbyteStateMessage withData(final JsonNode data) {
    this.serializedData = Jsons.serialize(data);
    return this;
  }
}
