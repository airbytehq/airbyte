/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.commons.text;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

public class NamesTest {

  @Test
  void testToAlphanumericAndUnderscore() {
    assertEquals("users", Names.toAlphanumericAndUnderscore("users"));
    assertEquals("users123", Names.toAlphanumericAndUnderscore("users123"));
    assertEquals("UsErS", Names.toAlphanumericAndUnderscore("UsErS"));
    assertEquals("users_USE_special_____", Names.toAlphanumericAndUnderscore("users USE special !@#$"));
  }

  @Test
  void testDoubleQuote() {
    assertEquals("\"abc\"", Names.doubleQuote("abc"));
    assertEquals("\"abc\"", Names.doubleQuote("\"abc\""));
    assertThrows(IllegalStateException.class, () -> Names.doubleQuote("\"abc"));
    assertThrows(IllegalStateException.class, () -> Names.doubleQuote("abc\""));
  }

  @Test
  void testSimpleQuote() {
    assertEquals("'abc'", Names.singleQuote("abc"));
    assertEquals("'abc'", Names.singleQuote("'abc'"));
    assertThrows(IllegalStateException.class, () -> Names.singleQuote("'abc"));
    assertThrows(IllegalStateException.class, () -> Names.singleQuote("abc'"));
  }

}
