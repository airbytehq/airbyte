/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import io.airbyte.integrations.destination.StandardNameTransformer;
import java.text.Normalizer;
import java.util.regex.Pattern;

public class S3NameTransformer extends StandardNameTransformer {

  // see https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
  private static final String S3_SAFE_CHARACTERS = "\\p{Alnum}/!_.*')(";
  private static final String S3_SPECIAL_CHARACTERS = "&$@=;:+,?-";
  private static final String S3_CHARACTER_PATTERN = "[^" + S3_SAFE_CHARACTERS + Pattern.quote(S3_SPECIAL_CHARACTERS) + "]";

  @Override
  public String convertStreamName(final String input) {
    return Normalizer.normalize(input, Normalizer.Form.NFKD)
        .replaceAll("\\p{M}", "") // P{M} matches a code point that is not a combining mark (unicode)
        .replaceAll(S3_CHARACTER_PATTERN, "_");
  }

}
