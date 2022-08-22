/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.enums;

import static io.airbyte.commons.enums.Enums.convertTo;
import static io.airbyte.commons.enums.Enums.isCompatible;
import static io.airbyte.commons.enums.Enums.toEnum;

import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class EnumsTest {

  enum E1 {
    TEST,
    TEST2
  }

  enum E2 {
    TEST
  }

  enum E3 {
    TEST,
    TEST2
  }

  enum E4 {
    TEST,
    TEST3
  }

  @Test
  void testConversion() {
    Assertions.assertEquals(E2.TEST, convertTo(E1.TEST, E2.class));
  }

  @Test
  void testConversionFails() {
    Assertions.assertThrows(IllegalArgumentException.class, () -> convertTo(E1.TEST2, E2.class));
  }

  @Test
  void testSelfCompatible() {
    Assertions.assertTrue(isCompatible(E1.class, E1.class));
  }

  @Test
  void testIsCompatible() {
    Assertions.assertTrue(isCompatible(E1.class, E3.class));
  }

  @Test
  void testNotCompatibleDifferentNames() {
    Assertions.assertFalse(isCompatible(E1.class, E4.class));
  }

  @Test
  void testNotCompatibleDifferentLength() {
    Assertions.assertFalse(isCompatible(E1.class, E4.class));
  }

  @Test
  void testNotCompatibleDifferentLength2() {
    Assertions.assertFalse(isCompatible(E4.class, E1.class));
  }

  enum E5 {
    VALUE_1,
    VALUE_TWO,
    value_three,
    value_4
  }

  @Test
  void testToEnum() {
    Assertions.assertEquals(Optional.of(E1.TEST), toEnum("test", E1.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_1), toEnum("VALUE_1", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_1), toEnum("value_1", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_TWO), toEnum("VALUE_TWO", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_TWO), toEnum("valuetwo", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_TWO), toEnum("valueTWO", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_TWO), toEnum("valueTWO$", E5.class));
    Assertions.assertEquals(Optional.of(E5.VALUE_TWO), toEnum("___valueTWO___", E5.class));
    Assertions.assertEquals(Optional.of(E5.value_three), toEnum("VALUE_THREE", E5.class));
    Assertions.assertEquals(Optional.of(E5.value_4), toEnum("VALUE_4", E5.class));
    Assertions.assertEquals(Optional.empty(), toEnum("VALUE_5", E5.class));
  }

}
