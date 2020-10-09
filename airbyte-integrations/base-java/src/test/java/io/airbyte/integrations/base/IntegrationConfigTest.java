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
import java.util.Optional;
import org.junit.jupiter.api.Test;

class IntegrationConfigTest {

  private static final Path CONFIG_PATH = Path.of("config.json");
  private static final Path CATALOG_PATH = Path.of("catalog.json");
  private static final Path STATE_PATH = Path.of("state.json");

  @Test
  void testSpec() {
    final IntegrationConfig config = IntegrationConfig.spec();
    assertEquals(Command.SPEC, config.getCommand());
    assertThrows(IllegalStateException.class, config::getConfigPath);
    assertThrows(IllegalStateException.class, config::getCatalogPath);
    assertThrows(IllegalStateException.class, config::getStatePath);
  }

  @Test
  void testCheck() {
    assertThrows(NullPointerException.class, () -> IntegrationConfig.check(null));

    final IntegrationConfig config = IntegrationConfig.check(CONFIG_PATH);
    assertEquals(Command.CHECK, config.getCommand());
    assertEquals(CONFIG_PATH, config.getConfigPath());
    assertThrows(IllegalStateException.class, config::getCatalogPath);
    assertThrows(IllegalStateException.class, config::getStatePath);
  }

  @Test
  void testDiscover() {
    assertThrows(NullPointerException.class, () -> IntegrationConfig.discover(null));

    final IntegrationConfig config = IntegrationConfig.discover(CONFIG_PATH);
    assertEquals(Command.DISCOVER, config.getCommand());
    assertEquals(CONFIG_PATH, config.getConfigPath());
    assertThrows(IllegalStateException.class, config::getCatalogPath);
    assertThrows(IllegalStateException.class, config::getStatePath);
  }

  @Test
  void testWrite() {
    assertThrows(NullPointerException.class, () -> IntegrationConfig.write(null, CATALOG_PATH));
    assertThrows(NullPointerException.class, () -> IntegrationConfig.write(CONFIG_PATH, null));

    final IntegrationConfig config = IntegrationConfig.write(CONFIG_PATH, CATALOG_PATH);
    assertEquals(Command.WRITE, config.getCommand());
    assertEquals(CONFIG_PATH, config.getConfigPath());
    assertEquals(CATALOG_PATH, config.getCatalogPath());
    assertThrows(IllegalStateException.class, config::getStatePath);
  }

  @Test
  void testReadWithState() {
    assertThrows(NullPointerException.class, () -> IntegrationConfig.read(null, CATALOG_PATH, STATE_PATH));
    assertThrows(NullPointerException.class, () -> IntegrationConfig.read(CONFIG_PATH, null, STATE_PATH));

    final IntegrationConfig config = IntegrationConfig.read(CONFIG_PATH, CATALOG_PATH, STATE_PATH);
    assertEquals(Command.READ, config.getCommand());
    assertEquals(CONFIG_PATH, config.getConfigPath());
    assertEquals(CATALOG_PATH, config.getCatalogPath());
    assertEquals(Optional.of(STATE_PATH), config.getStatePath());
  }

  @Test
  void testReadWithoutState() {
    assertThrows(NullPointerException.class, () -> IntegrationConfig.read(null, CATALOG_PATH, null));
    assertThrows(NullPointerException.class, () -> IntegrationConfig.read(CONFIG_PATH, null, null));

    final IntegrationConfig config = IntegrationConfig.read(CONFIG_PATH, CATALOG_PATH, null);
    assertEquals(Command.READ, config.getCommand());
    assertEquals(CONFIG_PATH, config.getConfigPath());
    assertEquals(CATALOG_PATH, config.getCatalogPath());
    assertEquals(Optional.empty(), config.getStatePath());
  }

}
