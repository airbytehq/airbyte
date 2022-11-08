/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.enums;

import com.google.common.base.Preconditions;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

public class Enums {

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> T2 convertTo(final T1 ie, final Class<T2> oe) {
    if (ie == null) {
      return null;
    }

    return Enum.valueOf(oe, ie.name());
  }

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> List<T2> convertListTo(final List<T1> ies, final Class<T2> oe) {
    return ies
        .stream()
        .map(ie -> convertTo(ie, oe))
        .collect(Collectors.toList());
  }

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> boolean isCompatible(final Class<T1> c1,
                                                                                final Class<T2> c2) {
    Preconditions.checkArgument(c1.isEnum());
    Preconditions.checkArgument(c2.isEnum());
    return c1.getEnumConstants().length == c2.getEnumConstants().length
        && Sets.difference(
            Arrays.stream(c1.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()),
            Arrays.stream(c2.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()))
            .isEmpty();
  }

  private static final Map<Class<?>, Map<String, ?>> NORMALIZED_ENUMS = Maps.newConcurrentMap();

  @SuppressWarnings("unchecked")
  public static <T extends Enum<T>> Optional<T> toEnum(final String value, final Class<T> enumClass) {
    Preconditions.checkArgument(enumClass.isEnum());

    if (!NORMALIZED_ENUMS.containsKey(enumClass)) {
      final T[] values = enumClass.getEnumConstants();
      final Map<String, T> mappings = Maps.newHashMapWithExpectedSize(values.length);
      for (final T t : values) {
        mappings.put(normalizeName(t.name()), t);
      }
      NORMALIZED_ENUMS.put(enumClass, mappings);
    }

    return Optional.ofNullable((T) NORMALIZED_ENUMS.get(enumClass).get(normalizeName(value)));
  }

  private static String normalizeName(final String name) {
    return name.toLowerCase().replaceAll("[^a-zA-Z0-9]", "");
  }

  public static <T1 extends Enum<T1>> Set<String> valuesAsStrings(final Class<T1> e) {
    Preconditions.checkArgument(e.isEnum());
    return Arrays.stream(e.getEnumConstants()).map(Enum::name).collect(Collectors.toSet());
  }

}
