/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.net.URI;
import lombok.SneakyThrows;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultToV0MigrationTest {

  AirbyteMessageMigrationV0 v0migration;

  @BeforeEach
  void beforeEach() {
    v0migration = new AirbyteMessageMigrationV0();
  }

  @Test
  void testVersionMetadata() {
    assertEquals("0", v0migration.getPreviousVersion().getMajorVersion());
    assertEquals("0", v0migration.getCurrentVersion().getMajorVersion());
  }

  @Test
  void testDowngrade() {
    final io.airbyte.protocol.models.v0.AirbyteMessage v0Message = getV0Message();

    final io.airbyte.protocol.models.AirbyteMessage downgradedMessage = v0migration.downgrade(v0Message);
    final io.airbyte.protocol.models.AirbyteMessage expectedMessage = getUnversionedMessage();
    assertEquals(expectedMessage, downgradedMessage);
  }

  @Test
  void testUpgrade() {
    final io.airbyte.protocol.models.AirbyteMessage unversionedMessage = getUnversionedMessage();

    final io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = v0migration.upgrade(unversionedMessage);
    final io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = getV0Message();
    assertEquals(expectedMessage, upgradedMessage);
  }

  @SneakyThrows
  private io.airbyte.protocol.models.v0.AirbyteMessage getV0Message() {
    return new io.airbyte.protocol.models.v0.AirbyteMessage()
        .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.SPEC)
        .withSpec(
            new io.airbyte.protocol.models.v0.ConnectorSpecification()
                .withProtocolVersion("0.3.0")
                .withDocumentationUrl(new URI("file:///tmp/doc")));
  }

  @SneakyThrows
  private io.airbyte.protocol.models.AirbyteMessage getUnversionedMessage() {
    return new io.airbyte.protocol.models.AirbyteMessage()
        .withType(io.airbyte.protocol.models.AirbyteMessage.Type.SPEC)
        .withSpec(
            new io.airbyte.protocol.models.ConnectorSpecification()
                .withProtocolVersion("0.3.0")
                .withDocumentationUrl(new URI("file:///tmp/doc")));
  }

}
