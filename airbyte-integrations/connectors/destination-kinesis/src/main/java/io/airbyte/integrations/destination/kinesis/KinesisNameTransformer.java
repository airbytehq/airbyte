/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.integrations.destination.StandardNameTransformer;

/**
 * KinesisNameTransformer class for creating Kinesis stream names.
 */
class KinesisNameTransformer extends StandardNameTransformer {

  /**
   * Create Kinesis destination stream name by combining the incoming namespace and stream
   *
   * @param namespace of the source data
   * @param stream of the source data
   */
  String streamName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    var streamName = namespace + "_" + stream;
    streamName = super.convertStreamName(streamName);
    // max char length for kinesis stream name is 128
    return streamName.length() > 128 ? streamName.substring(0, 128) : streamName;
  }

}
