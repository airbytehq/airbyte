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

package io.dataline.config;

import static org.mockito.Mockito.when;

import java.nio.file.Paths;
import java.util.function.Function;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class EnvConfigsTest {

  private Function<String, String> function;
  private EnvConfigs config;

  @BeforeEach
  void setUp() {
    function = Mockito.mock(Function.class);
    config = new EnvConfigs(function);
  }

  @Test
  void testGetEnvBehavior() {
    Assertions.assertNull(System.getenv("MY_RANDOM_VAR_1234"));
  }

  @Test
  void testGet() {
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals(Paths.get("abc/def"), config.getWorkspaceRoot());

    when(function.apply(EnvConfigs.CONFIG_ROOT)).thenReturn("a/b");
    Assertions.assertEquals(Paths.get("a/b"), config.getConfigRoot());
  }

  @Test
  void testMissing() {
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceRoot());

    when(function.apply(EnvConfigs.CONFIG_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getConfigRoot());
  }
}
