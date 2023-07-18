/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

public class TypingAndDedupingFlag {

  public static final boolean isDestinationV2() {
    return DestinationConfig.getInstance().getBooleanValue("use_1s1t_format");
  }

}
