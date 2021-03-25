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

package io.airbyte.commons.lang;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class ExceptionsTest {

  @Test
  void testToRuntime() {
    assertEquals("hello", Exceptions.toRuntime(() -> callable("hello", false)));
    assertThrows(RuntimeException.class, () -> Exceptions.toRuntime(() -> callable("goodbye", true)));
  }

  @Test
  void testToRuntimeVoid() {
    List<String> list = new ArrayList<>();
    assertThrows(RuntimeException.class, () -> Exceptions.toRuntime(() -> voidCallable(list, "hello", true)));
    assertEquals(0, list.size());

    Exceptions.toRuntime(() -> voidCallable(list, "goodbye", false));
    assertEquals(1, list.size());
    assertEquals("goodbye", list.get(0));
  }

  @Test
  void testSwallow() {
    Exceptions.swallow(() -> {
      throw new RuntimeException();
    });
    Exceptions.swallow(() -> {
      throw new Exception();
    });
  }

  private String callable(String input, boolean shouldThrow) throws IOException {
    if (shouldThrow) {
      throw new IOException();
    } else {
      return input;
    }
  }

  private void voidCallable(List<String> list, String input, boolean shouldThrow) throws IOException {
    if (shouldThrow) {
      throw new IOException();
    } else {
      list.add(input);
    }
  }

}
