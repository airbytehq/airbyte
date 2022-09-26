/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.util.HashSet;
import javax.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest
class AirbyteMessageMigratorMicronautTest {

  @Inject
  AirbyteMessageMigrator messageMigrator;

  @Test
  void testMigrationInjection() {
    // This should contain the list of all the supported majors of the airbyte protocol except the most
    // recent one since the migrations themselves are keyed on the lower version.
    assertEquals(new HashSet<>(), messageMigrator.getMigrationKeys());
  }

}
