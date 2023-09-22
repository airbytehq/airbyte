/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class SqlGeneratorUtils {

  public static String wrap(final String open, final String content, final String close) {
    return open + content + close;
  }

  public static String cast(final String content, final String asType, boolean useSafeCast) {
    final var open = useSafeCast ? "SAFE_CAST(" : "CAST(";
    return wrap(open, content + " as " + asType, ")");
  }

  public static String cast(final String content, final String asType) {
    return cast(content, asType, false);
  }

}
