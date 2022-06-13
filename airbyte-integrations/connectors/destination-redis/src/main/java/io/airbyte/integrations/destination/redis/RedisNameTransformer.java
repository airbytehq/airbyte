/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

class RedisNameTransformer {

  String keyName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    return namespace + ":" + stream;
  }

  String tmpKeyName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    return "tmp:" + namespace + ":" + stream;
  }

}
