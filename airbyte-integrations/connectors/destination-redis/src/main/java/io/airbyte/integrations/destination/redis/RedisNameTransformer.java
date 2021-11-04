/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.StandardNameTransformer;

class RedisNameTransformer extends StandardNameTransformer {

  String outputNamespace(String namespace) {
    return namespace == null || namespace.isBlank() ? "" : Names.toAlphanumericAndUnderscore(namespace);
  }

  String outputKey(String streamName) {
    return super.getRawTableName(streamName);
  }

  String outputTmpKey(String streamName) {
    return super.getTmpTableName(streamName);
  }

}
