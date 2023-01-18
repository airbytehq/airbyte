/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import java.util.HashSet;
import java.util.List;
import org.junit.jupiter.api.Test;

@MicronautTest
class AirbyteMessageMigratorMicronautTest {

  @Inject
  AirbyteMessageMigrator messageMigrator;

  @Test
  void testMigrationInjection() {
    // This should contain the list of all the supported majors of the airbyte protocol except the most
    // recent one since the migrations themselves are keyed on the lower version.
    assertEquals(new HashSet<>(List.of("0")), messageMigrator.getMigrationKeys());
  }

}
