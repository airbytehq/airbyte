/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.type;

import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

public class Types {

  /**
   * Convenience method converting a list to a list of lists of the same type. Each item in the
   * original list is inserted into its own list.
   */
  public static <T> List<List<T>> boxToListofList(final List<T> list) {
    final var nonNullEntries = list.stream().filter(Objects::nonNull);
    return nonNullEntries.map(Collections::singletonList).collect(Collectors.toList());
  }

}
