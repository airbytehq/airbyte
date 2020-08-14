package io.dataline.commons.enums;

public class Enums {

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> T2 convertTo(T1 ie, Class<T2> oe) {
    return Enum.valueOf(oe, ie.name());
  }
}
