/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import org.apache.commons.lang3.StringUtils;

public class KeenCharactersStripper {

  // Keen collection names can't contain some special characters like non ascii accented characters
  // while Kafka Topic names can't contain some other set of special characters, with except for -._
  // and whitespace characters
  public static String stripSpecialCharactersFromStreamName(final String streamName) {
    return StringUtils.stripAccents(streamName).replaceAll("[^A-Za-z0-9 -._]", "");
  }

}
