/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
