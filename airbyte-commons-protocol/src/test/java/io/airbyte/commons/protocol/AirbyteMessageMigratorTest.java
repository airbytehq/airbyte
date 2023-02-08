/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.protocol.migrations.AirbyteMessageMigration;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AirbyteMessageMigratorTest {

  static final Version v0 = new Version("0.0.0");
  static final Version v1 = new Version("1.0.0");
  static final Version v2 = new Version("2.0.0");

  record ObjectV0(String name0) {}

  record ObjectV1(String name1) {}

  record ObjectV2(String name2) {}

  static class Migrate0to1 implements AirbyteMessageMigration<ObjectV0, ObjectV1> {

    @Override
    public ObjectV0 downgrade(ObjectV1 message, Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
      return new ObjectV0(message.name1);
    }

    @Override
    public ObjectV1 upgrade(ObjectV0 message, Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
      return new ObjectV1(message.name0);
    }

    @Override
    public Version getPreviousVersion() {
      return v0;
    }

    @Override
    public Version getCurrentVersion() {
      return v1;
    }

  }

  static class Migrate1to2 implements AirbyteMessageMigration<ObjectV1, ObjectV2> {

    @Override
    public ObjectV1 downgrade(ObjectV2 message, Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
      return new ObjectV1(message.name2);
    }

    @Override
    public ObjectV2 upgrade(ObjectV1 message, Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
      return new ObjectV2(message.name1);
    }

    @Override
    public Version getPreviousVersion() {
      return v1;
    }

    @Override
    public Version getCurrentVersion() {
      return v2;
    }

  }

  AirbyteMessageMigrator migrator;

  @BeforeEach
  void beforeEach() {
    migrator = new AirbyteMessageMigrator(
        List.of(new Migrate0to1(), new Migrate1to2()));
    migrator.initialize();
  }

  @Test
  void testDowngrade() {
    final ObjectV2 obj = new ObjectV2("my name");

    final ObjectV0 objDowngradedTo0 = migrator.downgrade(obj, v0, Optional.empty());
    assertEquals(obj.name2, objDowngradedTo0.name0);

    final ObjectV1 objDowngradedTo1 = migrator.downgrade(obj, v1, Optional.empty());
    assertEquals(obj.name2, objDowngradedTo1.name1);

    final ObjectV2 objDowngradedTo2 = migrator.downgrade(obj, v2, Optional.empty());
    assertEquals(obj.name2, objDowngradedTo2.name2);
  }

  @Test
  void testUpgrade() {
    final ObjectV0 obj0 = new ObjectV0("my name 0");
    final ObjectV2 objUpgradedFrom0 = migrator.upgrade(obj0, v0, Optional.empty());
    assertEquals(obj0.name0, objUpgradedFrom0.name2);

    final ObjectV1 obj1 = new ObjectV1("my name 1");
    final ObjectV2 objUpgradedFrom1 = migrator.upgrade(obj1, v1, Optional.empty());
    assertEquals(obj1.name1, objUpgradedFrom1.name2);

    final ObjectV2 obj2 = new ObjectV2("my name 2");
    final ObjectV2 objUpgradedFrom2 = migrator.upgrade(obj2, v2, Optional.empty());
    assertEquals(obj2.name2, objUpgradedFrom2.name2);
  }

  @Test
  void testUnsupportedDowngradeShouldFailExplicitly() {
    assertThrows(RuntimeException.class, () -> {
      migrator.downgrade(new ObjectV2("woot"), new Version("5.0.0"), Optional.empty());
    });
  }

  @Test
  void testUnsupportedUpgradeShouldFailExplicitly() {
    assertThrows(RuntimeException.class, () -> {
      migrator.upgrade(new ObjectV0("woot"), new Version("4.0.0"), Optional.empty());
    });
  }

  @Test
  void testRegisterCollisionsShouldFail() {
    assertThrows(RuntimeException.class, () -> {
      migrator = new AirbyteMessageMigrator(
          List.of(new Migrate0to1(), new Migrate1to2(), new Migrate0to1()));
      migrator.initialize();
    });
  }

}
