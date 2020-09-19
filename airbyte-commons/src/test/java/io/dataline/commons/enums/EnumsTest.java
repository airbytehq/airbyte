/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

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
