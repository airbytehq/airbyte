/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableList;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.List;
import org.junit.jupiter.api.Test;

public class MigrateTest {

  @Test
  void testGetPreviousMigration() {
    final List<AirbyteVersion> versions = ImmutableList.of(
        new AirbyteVersion("0.14.0"),
        new AirbyteVersion("0.14.1"),
        new AirbyteVersion("0.14.4"),
        new AirbyteVersion("0.15.0"));
    assertEquals(0, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.0")));
    assertEquals(1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.1")));
    assertEquals(1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.3")));
    assertEquals(2, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.4")));
    assertEquals(2, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.14.5")));
    assertEquals(3, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.15.0")));
    assertEquals(-1, Migrate.getPreviousMigration(versions, new AirbyteVersion("0.16.0")));
  }

}
