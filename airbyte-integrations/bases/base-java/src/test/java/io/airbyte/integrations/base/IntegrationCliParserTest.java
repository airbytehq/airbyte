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

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class IntegrationCliParserTest {

  private static final String CONFIG_FILENAME = "config.json";
  private static final String CATALOG_FILENAME = "catalog.json";
  private static final String STATE_FILENAME = "state.json";

  @Test
  void testSpec() {
    final String[] args = new String[] {"--spec"};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.spec(), actual);
  }

  @Test
  void testCheck() {
    final String[] args = new String[] {"--check", "--config", CONFIG_FILENAME};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.check(Path.of(CONFIG_FILENAME)), actual);
  }

  @Test
  void testDiscover() {
    final String[] args = new String[] {"--discover", "--config", CONFIG_FILENAME};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.discover(Path.of(CONFIG_FILENAME)), actual);
  }

  @Test
  void testWrite() {
    final String[] args = new String[] {"--write", "--config", CONFIG_FILENAME, "--catalog", CATALOG_FILENAME};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.write(Path.of(CONFIG_FILENAME), Path.of(CATALOG_FILENAME)), actual);
  }

  @Test
  void testReadWithoutState() {
    final String[] args = new String[] {"--read", "--config", CONFIG_FILENAME, "--catalog", CATALOG_FILENAME};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.read(Path.of(CONFIG_FILENAME), Path.of(CATALOG_FILENAME), null), actual);
  }

  @Test
  void testReadWithState() {
    final String[] args = new String[] {"--read", "--config", CONFIG_FILENAME, "--catalog", CATALOG_FILENAME, "--state", STATE_FILENAME};
    final IntegrationConfig actual = new IntegrationCliParser().parse(args);
    assertEquals(IntegrationConfig.read(Path.of(CONFIG_FILENAME), Path.of(CATALOG_FILENAME), Path.of(STATE_FILENAME)), actual);
  }

  @Test
  void testFailsOnUnknownArg() {
    final String[] args = new String[] {"--check", "--config", CONFIG_FILENAME, "--random", "garbage"};
    assertThrows(IllegalArgumentException.class, () -> new IntegrationCliParser().parse(args));
  }

}
