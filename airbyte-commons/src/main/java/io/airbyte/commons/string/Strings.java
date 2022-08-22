/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.string;

import com.google.common.collect.Streams;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;

public class Strings {

  public static String join(final Iterable<?> iterable, final CharSequence separator) {
    return Streams.stream(iterable)
        .map(Object::toString)
        .collect(Collectors.joining(separator));
  }

  public static String addRandomSuffix(final String base, final String separator, final int suffixLength) {
    return base + separator + RandomStringUtils.randomAlphabetic(suffixLength).toLowerCase();
  }

  public static String safeTrim(final String string) {
    return string == null ? null : string.trim();
  }

}
