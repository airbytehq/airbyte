/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import java.util.Optional;
import java.util.function.Predicate;

public class TypingAndDedupingFlag {

  public static boolean isDestinationV2() {
    return DestinationConfig.getInstance().getBooleanValue("use_1s1t_format");
  }

  public static Optional<String> getRawNamespaceOverride(String option) {
    return Optional.ofNullable(DestinationConfig.getInstance().getTextValue(option))
                   .filter(Predicate.not(String::isEmpty));
  }

}
