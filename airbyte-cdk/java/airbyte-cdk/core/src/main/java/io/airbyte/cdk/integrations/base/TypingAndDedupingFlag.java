/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import java.util.Optional;

public class TypingAndDedupingFlag {

  public static boolean isDestinationV2() {
    return DestinationConfig.getInstance().getIsV2Destination()
        || DestinationConfig.getInstance().getBooleanValue("use_1s1t_format");
  }

  public static Optional<String> getRawNamespaceOverride(final String option) {
    final String rawOverride = DestinationConfig.getInstance().getTextValue(option);
    if (rawOverride == null || rawOverride.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(rawOverride);
    }
  }

}
