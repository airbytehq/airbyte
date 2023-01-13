/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class RedpandaNameTransformer extends StandardNameTransformer {

  String topicName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    var streamName = namespace + "_" + stream;
    streamName = super.convertStreamName(streamName);
    // max char length for redpanda topic name is 255
    return streamName.length() > 255 ? streamName.substring(0, 255) : streamName;
  }

}
