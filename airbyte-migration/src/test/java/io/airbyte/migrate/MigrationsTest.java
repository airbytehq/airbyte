/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.version.AirbyteVersion;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class MigrationsTest {

  @Test
  void testMigrationsOrder() {
    final List<Migration> migrationsSorted = Migrations.MIGRATIONS.stream()
        .sorted((a, b) -> new AirbyteVersion(a.getVersion()).patchVersionCompareTo(new AirbyteVersion(b.getVersion())))
        .collect(Collectors.toList());
    assertEquals(migrationsSorted, Migrations.MIGRATIONS, "Migrations must be added to the MIGRATIONS list in version order.");
  }

}
