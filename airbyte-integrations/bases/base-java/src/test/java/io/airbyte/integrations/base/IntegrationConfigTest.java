/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
