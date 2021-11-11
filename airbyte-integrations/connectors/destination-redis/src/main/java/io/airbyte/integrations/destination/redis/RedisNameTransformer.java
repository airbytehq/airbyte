/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.StandardNameTransformer;

class RedisNameTransformer extends StandardNameTransformer {

  String keyName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    var keyName = namespace + "_" + stream;
    return Names.toAlphanumericAndUnderscore(keyName);
  }

  String tmpKeyName(String namespace, String stream) {
    namespace = namespace != null ? namespace : "";
    var keyName = "tmp_" + namespace + "_" + stream;
    return Names.toAlphanumericAndUnderscore(keyName);
  }

}
