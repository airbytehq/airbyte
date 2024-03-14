/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.deser;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.apache.commons.lang3.tuple.ImmutablePair;

public interface StreamAwareDataTransformer {

  /**
   * Transforms the input data by applying destination limitations and populating
   * {@link AirbyteRecordMessageMeta}. The returned pair contains the transformed data and the merged
   * meta information from upstream.
   *
   * @param streamDescriptor
   * @param data
   * @param meta
   * @return
   */
  ImmutablePair<JsonNode, AirbyteRecordMessageMeta> transform(StreamDescriptor streamDescriptor, JsonNode data, AirbyteRecordMessageMeta meta);

}
