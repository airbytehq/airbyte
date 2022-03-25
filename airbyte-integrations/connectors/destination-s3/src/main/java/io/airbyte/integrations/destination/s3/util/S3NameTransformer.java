/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import java.text.Normalizer;

/**
 * When choosing identifiers names in destinations, extended Names can handle more special
 * characters than standard Names by using the quoting characters: "..."
 *
 * This class detects when such special characters are used and adds the appropriate quoting when
 * necessary.
 */
public class S3NameTransformer extends ExtendedNameTransformer {

  // Symbols "=" and "-" are required for AWS Glue crawler
  // more details https://docs.aws.amazon.com/glue/latest/dg/crawler-s3-folder-table-partition.html
  public static final String NON_ALPHANUMERIC_AND_UNDERSCORE_DASH_EQUAL_PATTERN = "[^\\p{Alnum}_=-]";

  /**
   * Converts any UTF8 string to a string with only alphanumeric and "=", "-" and "_" characters
   * without preserving accent characters.
   *
   * @param input string to convert
   * @return cleaned string
   */
  public String convertStreamName(final String input) {
    if (input.contains("=")) {
      // case AWS Glue crawler
      // more details https://docs.aws.amazon.com/glue/latest/dg/crawler-s3-folder-table-partition.html
      return Normalizer.normalize(input, Normalizer.Form.NFKD)
          .replaceAll("\\p{M}", "")
          .replaceAll("\\s+", "_")
          .replaceAll(NON_ALPHANUMERIC_AND_UNDERSCORE_DASH_EQUAL_PATTERN, "_");
    } else {
      return super.convertStreamName(input);
    }

  }

}
