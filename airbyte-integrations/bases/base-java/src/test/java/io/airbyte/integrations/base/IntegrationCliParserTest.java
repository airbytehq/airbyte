/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
