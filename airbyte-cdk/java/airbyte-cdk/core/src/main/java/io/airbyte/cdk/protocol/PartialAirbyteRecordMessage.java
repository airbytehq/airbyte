package io.airbyte.cdk.protocol;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Map;
import java.util.Objects;

public class PartialAirbyteRecordMessage {

  String namespace;
  String stream;
  String serializedData;
  Long emittedAt;

  public static PartialAirbyteRecordMessage fromJson(final StringIterator message) {
    final PartialAirbyteRecordMessage record = new PartialAirbyteRecordMessage();
    final boolean nonNull = PartialJsonDeserializer.processObject(
        message,
        Map.of(
            "data", (recordDataIterator) -> record.serializedData = PartialJsonDeserializer.readSerializedValue(recordDataIterator),
            "namespace", (recordNamespaceIterator) -> record.namespace = PartialJsonDeserializer.readStringValue(recordNamespaceIterator),
            "stream", (recordStreamIterator) -> record.stream = PartialJsonDeserializer.readStringValue(recordStreamIterator),
            "emitted_at", (recordStreamIterator) -> record.emittedAt = (Long) PartialJsonDeserializer.readNumber(recordStreamIterator)
        )
    );
    if (nonNull) {
      return record;
    } else {
      return null;
    }
  }

  public String getNamespace() {
    return namespace;
  }

  public String getStream() {
    return stream;
  }

  public String getSerializedData() {
    return serializedData;
  }

  public Long getEmittedAt() {
    return emittedAt;
  }

  @Override
  public String toString() {
    return "PartialAirbyteRecordMessage{" +
        "namespace='" + namespace + '\'' +
        ", stream='" + stream + '\'' +
        ", serializedData='" + serializedData + '\'' +
        ", emittedAt=" + emittedAt +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;

    final PartialAirbyteRecordMessage that = (PartialAirbyteRecordMessage) o;

    if (!Objects.equals(namespace, that.namespace)) return false;
    if (!Objects.equals(stream, that.stream)) return false;
    if (!Objects.equals(serializedData, that.serializedData))
      return false;
    return Objects.equals(emittedAt, that.emittedAt);
  }

  @Override
  public int hashCode() {
    int result = namespace != null ? namespace.hashCode() : 0;
    result = 31 * result + (stream != null ? stream.hashCode() : 0);
    result = 31 * result + (serializedData != null ? serializedData.hashCode() : 0);
    result = 31 * result + (emittedAt != null ? emittedAt.hashCode() : 0);
    return result;
  }

  public void setNamespace(final String namespace) {
    this.namespace = namespace;
  }

  public PartialAirbyteRecordMessage withEmittedAt(final long emittedAt) {
    this.emittedAt = emittedAt;
    return this;
  }

  public String serialize() {
    String output = "{";
    output += "\"data\": " + serializedData;
    output += ", \"namespace\": \"" + namespace + "\"";
    output += ", \"stream\": \"" + stream + "\"";
    output += ", \"emitted_at\": " + emittedAt;
    output += "}";
    return output;
  }

  public AirbyteRecordMessage toFullRecordMessage() {
    final AirbyteRecordMessage fullRecordMessage = new AirbyteRecordMessage();
    fullRecordMessage.setNamespace(namespace);
    fullRecordMessage.setStream(stream);
    fullRecordMessage.setEmittedAt(emittedAt);
    fullRecordMessage.setData(Jsons.deserializeExact(serializedData));
    return fullRecordMessage;
  }

  public AirbyteStreamNameNamespacePair toStreamNameNamespacePair() {
    return new AirbyteStreamNameNamespacePair(stream, namespace);
  }

  public PartialAirbyteRecordMessage withStream(final String stream) {
    this.stream = stream;
    return this;
  }

  public PartialAirbyteRecordMessage withNamespace(final String namespace) {
    this.namespace = namespace;
    return this;
  }

  public PartialAirbyteRecordMessage withData(final JsonNode data) {
    this.serializedData = Jsons.serialize(data);
    return this;
  }

  public PartialAirbyteRecordMessage withSerializedData(final String serializedData) {
    this.serializedData = serializedData;
    return this;
  }
}
