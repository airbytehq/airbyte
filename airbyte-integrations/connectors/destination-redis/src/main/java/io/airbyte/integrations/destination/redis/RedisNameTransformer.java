package io.airbyte.integrations.destination.redis;

import io.airbyte.integrations.destination.StandardNameTransformer;

class RedisNameTransformer extends StandardNameTransformer {

    String outputKey(String streamName) {
        return super.getRawTableName(streamName);
    }

    String outputTmpKey(String streamName) {
        return super.getTmpTableName(streamName);
    }

}
