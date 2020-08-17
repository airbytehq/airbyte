package io.dataline.commons.enums;

import static io.dataline.commons.enums.Enums.convertTo;
import static io.dataline.commons.enums.Enums.isCompatible;

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
  public void testConversion() {
    Assertions.assertEquals(E2.TEST, convertTo(E1.TEST, E2.class));
  }

  @Test
  public void testConversionFails() {
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
}
