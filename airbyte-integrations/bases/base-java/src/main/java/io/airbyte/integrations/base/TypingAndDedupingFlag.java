/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import java.util.Optional;
import org.elasticsearch.common.Strings;

public class TypingAndDedupingFlag {

  public static final String RAW_DATA_DATASET = "raw_data_dataset";

  public static boolean isDestinationV2() {
    return DestinationConfig.getInstance().getBooleanValue("use_1s1t_format");
  }

  public static Optional<String> getRawNamespaceOverride() {
    String rawOverride = DestinationConfig.getInstance().getTextValue(RAW_DATA_DATASET);
    if (Strings.isEmpty(rawOverride)) {
      return Optional.empty();
    } else {
      return Optional.of(rawOverride);
    }
  }

}
