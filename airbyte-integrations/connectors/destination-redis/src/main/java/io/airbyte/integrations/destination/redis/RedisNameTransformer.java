package io.airbyte.integrations.destination.redis;

import com.google.common.base.CharMatcher;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.StandardNameTransformer;

class RedisNameTransformer extends StandardNameTransformer {

    String outputNamespace(String namespace) {
        if (namespace == null || namespace.isBlank()) {
            return "default";
        }
        return CharMatcher.is('_').trimLeadingFrom(Names.toAlphanumericAndUnderscore(namespace));
    }

    String outputKey(String streamName) {
        return super.getRawTableName(streamName);
    }

    String outputTmpKey(String streamName) {
        return super.getTmpTableName(streamName);
    }

}
