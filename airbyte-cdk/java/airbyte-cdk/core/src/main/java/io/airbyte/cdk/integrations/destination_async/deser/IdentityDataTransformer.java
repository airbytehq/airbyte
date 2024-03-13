/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.deser;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.apache.commons.lang3.tuple.ImmutablePair;

/**
 * Identity transformer which echoes back the original data and meta.
 */
public class IdentityDataTransformer implements StreamAwareDataTransformer {

  @Override
  public ImmutablePair<JsonNode, AirbyteRecordMessageMeta> transform(StreamDescriptor streamDescriptor,
                                                                     JsonNode data,
                                                                     AirbyteRecordMessageMeta meta) {
    return ImmutablePair.of(data, meta);
  }

}
