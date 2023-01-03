/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.map;

import com.google.common.base.Preconditions;
import java.util.HashMap;
import java.util.Map;

public class MoreMaps {

  @SafeVarargs
  public static <K, V> Map<K, V> merge(final Map<K, V>... maps) {
    final Map<K, V> outputMap = new HashMap<>();

    for (final Map<K, V> map : maps) {
      Preconditions.checkNotNull(map);
      outputMap.putAll(map);
    }

    return outputMap;
  }

}
