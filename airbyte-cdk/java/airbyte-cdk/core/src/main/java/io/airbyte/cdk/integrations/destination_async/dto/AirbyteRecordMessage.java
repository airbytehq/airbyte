package io.airbyte.cdk.integrations.destination_async.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import lombok.Getter;
import lombok.Setter;

@Getter
public class AirbyteRecordMessage {


  private final String namespace;

  private final String stream;

  private final String data;

  private final long emittedAt;

  private final AirbyteRecordMessageMeta meta;

  public AirbyteRecordMessage(final String namespace, final  String stream, final String data, final long emittedAt, final AirbyteRecordMessageMeta meta) {
    this.namespace = namespace;
    this.stream = stream;
    this.data = data;
    this.emittedAt = emittedAt;
    this.meta = meta;
  }

}
