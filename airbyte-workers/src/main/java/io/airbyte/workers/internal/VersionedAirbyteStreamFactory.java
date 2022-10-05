/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigrator;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.protocol.serde.AirbyteMessageDeserializer;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Extends DefaultAirbyteStreamFactory to handle version specific conversions.
 *
 * A VersionedAirbyteStreamFactory handles parsing and validation from a specific version of the
 * Airbyte Protocol as well as upgrading messages to the current version.
 */
public class VersionedAirbyteStreamFactory<T> extends DefaultAirbyteStreamFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(VersionedAirbyteStreamFactory.class);

  private final AirbyteMessageDeserializer<T> deserializer;
  private final AirbyteMessageVersionedMigrator<T> migrator;
  private final Version protocolVersion;

  public VersionedAirbyteStreamFactory(final AirbyteMessageSerDeProvider serDeProvider,
                                       final AirbyteMessageVersionedMigratorFactory migratorFactory,
                                       final Version protocolVersion) {
    this(serDeProvider, migratorFactory, protocolVersion, MdcScope.DEFAULT_BUILDER);
  }

  public VersionedAirbyteStreamFactory(final AirbyteMessageSerDeProvider serDeProvider,
                                       final AirbyteMessageVersionedMigratorFactory migratorFactory,
                                       final Version protocolVersion,
                                       final MdcScope.Builder containerLogMdcBuilder) {
    // TODO AirbyteProtocolPredicate needs to be updated to be protocol version aware
    super(new AirbyteProtocolPredicate(), LOGGER, containerLogMdcBuilder);
    this.deserializer = (AirbyteMessageDeserializer<T>) serDeProvider.getDeserializer(protocolVersion).orElseThrow();
    this.migrator = migratorFactory.getVersionedMigrator(protocolVersion);
    this.protocolVersion = protocolVersion;
  }

  @Override
  protected Stream<AirbyteMessage> toAirbyteMessage(final JsonNode json) {
    try {
      final io.airbyte.protocol.models.v0.AirbyteMessage message = migrator.upgrade(deserializer.deserialize(json));
      return Stream.of(convert(message));
    } catch (RuntimeException e) {
      LOGGER.warn("Failed to upgrade a message from version {}: {}", protocolVersion, Jsons.serialize(json));
      return Stream.empty();
    }
  }

  // TODO remove this conversion once we migrated default AirbyteMessage to be from a versioned
  // namespace
  private AirbyteMessage convert(final io.airbyte.protocol.models.v0.AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
  }

}
