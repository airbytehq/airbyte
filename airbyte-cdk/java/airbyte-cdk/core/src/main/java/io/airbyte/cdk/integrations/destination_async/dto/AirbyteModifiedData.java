package io.airbyte.cdk.integrations.destination_async.dto;

import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import lombok.Getter;
import lombok.Setter;

@Getter
public class AirbyteModifiedData {

  private final String data;

  private final AirbyteRecordMessageMeta meta;

  public AirbyteModifiedData(String data, AirbyteRecordMessageMeta meta) {
    this.data = data;
    this.meta = meta;
  }

}
