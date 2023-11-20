package io.airbyte.cdk.protocol;

import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

public class PartialAirbyteMessage {
  AirbyteMessage.Type type;
  PartialAirbyteRecordMessage record;
  PartialAirbyteStateMessage state;

  public static Optional<PartialAirbyteMessage> tryFromJson(final String message) {
    try {
      return Optional.of(fromJson(new StringIterator(message)));
    } catch (final Exception e) {
      return Optional.empty();
    }
  }

  public static PartialAirbyteMessage fromJson(final String message) {
    return fromJson(new StringIterator(message));
  }

  public static PartialAirbyteMessage fromJson(final StringIterator message) {
    final PartialAirbyteMessage deserMessage = new PartialAirbyteMessage();
    final boolean nonNull = PartialJsonDeserializer.processObject(
        message,
        Map.of(
            "type", (messageTypeIterator) -> deserMessage.type = AirbyteMessage.Type.valueOf(PartialJsonDeserializer.readStringValue(messageTypeIterator)),
            "record", (messageRecordIterator) -> deserMessage.record = PartialAirbyteRecordMessage.fromJson(messageRecordIterator),
            "state", (messageStateIterator) -> deserMessage.state = PartialAirbyteStateMessage.fromJson(messageStateIterator)
        )
    );
    if (nonNull) {
      return deserMessage;
    } else {
      return null;
    }
  }

  public AirbyteMessage.Type getType() {
    return type;
  }

  public PartialAirbyteRecordMessage getRecord() {
    return record;
  }

  public PartialAirbyteStateMessage getState() {
    return state;
  }

  @Override
  public String toString() {
    return "PartialAirbyteMessage{" +
        "type=" + type +
        ", record=" + record +
        ", state=" + state +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;

    final PartialAirbyteMessage that = (PartialAirbyteMessage) o;

    if (type != that.type) return false;
    if (!Objects.equals(record, that.record)) return false;
    return Objects.equals(state, that.state);
  }

  @Override
  public int hashCode() {
    int result = type != null ? type.hashCode() : 0;
    result = 31 * result + (record != null ? record.hashCode() : 0);
    result = 31 * result + (state != null ? state.hashCode() : 0);
    return result;
  }

  public String serialize() {
    String output = "{";
    output += "\"type\": \"" + type + "\"";
    if (record != null) {
      output += ", \"record\": " + record.serialize();
    }
    if (state != null) {
      output += ", \"state\": " + state.serialize();
    }
    output += "}";
    return output;
  }

  public AirbyteMessage toFullMessage() {
    final AirbyteMessage fullMessage = new AirbyteMessage();
    fullMessage.setType(type);
    if (record != null) {
      fullMessage.setRecord(record.toFullRecordMessage());
    }
    if (state != null) {
      fullMessage.setState(state.toFullStateMessage());
    }
    return fullMessage;
  }

  public PartialAirbyteMessage withType(final AirbyteMessage.Type type) {
    this.type = type;
    return this;
  }

  public PartialAirbyteMessage withRecord(final PartialAirbyteRecordMessage record) {
    this.record = record;
    return this;
  }

  public PartialAirbyteMessage withState(final PartialAirbyteStateMessage state) {
    this.state = state;
    return this;
  }
}
