/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import java.util.Set;
import org.junit.jupiter.api.Test;

@MicronautTest
class MigratorsMicronautTest {

  @Inject
  AirbyteMessageMigrator messageMigrator;

  @Inject
  ConfiguredAirbyteCatalogMigrator configuredAirbyteCatalogMigrator;

  // This should contain the list of all the supported majors of the airbyte protocol except the most
  // recent one since the migrations themselves are keyed on the lower version.
  final Set<String> SUPPORTED_VERSIONS = Set.of("0");

  @Test
  void testAirbyteMessageMigrationInjection() {
    assertEquals(SUPPORTED_VERSIONS, messageMigrator.getMigrationKeys());
  }

  @Test
  void testConfiguredAirbyteCatalogMigrationInjection() {
    assertEquals(SUPPORTED_VERSIONS, configuredAirbyteCatalogMigrator.getMigrationKeys());
  }

}
