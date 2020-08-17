package io.dataline.commons.enums;

import com.google.common.base.Preconditions;
import com.google.common.collect.Sets;
import java.util.Arrays;
import java.util.stream.Collectors;

public class Enums {

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> T2 convertTo(T1 ie, Class<T2> oe) {
    return Enum.valueOf(oe, ie.name());
  }

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> boolean isCompatible(
      Class<T1> c1, Class<T2> c2) {
    Preconditions.checkArgument(c1.isEnum());
    Preconditions.checkArgument(c2.isEnum());
    return c1.getEnumConstants().length == c2.getEnumConstants().length
        && Sets.difference(
                Arrays.stream(c1.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()),
                Arrays.stream(c2.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()))
            .isEmpty();
  }
}
