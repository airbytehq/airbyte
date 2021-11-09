package io.airbyte.integrations.destination.kinesis;

import io.airbyte.integrations.destination.StandardNameTransformer;

class KinesisNameTransformer extends StandardNameTransformer {

    String streamName(String namespace, String stream) {
        namespace = namespace != null ? namespace : "";
        var streamName = namespace + "_" + stream;
        streamName = super.convertStreamName(streamName);
        // max char length for kinesis stream name is 128
        return streamName.length() > 128 ? streamName.substring(0, 128) : streamName;
    }

}
