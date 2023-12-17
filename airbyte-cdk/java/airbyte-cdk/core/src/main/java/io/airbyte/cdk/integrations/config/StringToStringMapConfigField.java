/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.config;

import com.google.common.collect.Maps;
import io.airbyte.commons.exceptions.ConfigErrorException;
import java.util.HashMap;
import java.util.Map;

class StringToStringMapConfigField<CONFIG_TYPE extends AirbyteConfig> extends ConfigField<CONFIG_TYPE, Map<String, String>> {

  StringToStringMapConfigField(String fieldName) {
    super(fieldName);
  }

  Map<String, String> convert(CONFIG_TYPE config) {
    return convert(config, this);
  }

  static <CONFIG_TYPE extends AirbyteConfig> Map<String, String> convert(CONFIG_TYPE config, StringToStringMapConfigField<CONFIG_TYPE> field) {
    String fieldValue = config.get(field).asText();
    if (config.has(field)) {
      final Map<String, String> parameters = new HashMap<>();
      if (!fieldValue.isBlank()) {
        final String[] keyValuePairs = fieldValue.split("&");
        for (final String kv : keyValuePairs) {
          final String[] split = kv.split("=");
          if (split.length == 2) {
            parameters.put(split[0], split[1]);
          } else {
            throw new ConfigErrorException(field.fieldName +
                " must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got "
                + fieldValue);
          }
        }
      }
      return parameters;
    } else {
      return Maps.newHashMap();
    }
  }

}
