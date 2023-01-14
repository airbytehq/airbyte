/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigrator;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.protocol.serde.AirbyteMessageDeserializer;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Stream;
import lombok.SneakyThrows;
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
  private static final Version fallbackVersion = new Version("0.2.0");

  // Buffer size to use when detecting the protocol version.
  // Given that BufferedReader::reset fails if we try to reset if we go past its buffer size, this
  // buffer has to be big enough to contain our longest spec and whatever messages get emitted before
  // the SPEC.
  private static final int BUFFER_READ_AHEAD_LIMIT = 32000;
  private static final int MESSAGES_LOOK_AHEAD_FOR_DETECTION = 10;
  private static final String TYPE_FIELD_NAME = "type";

  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteMessageVersionedMigratorFactory migratorFactory;
  private AirbyteMessageDeserializer<T> deserializer;
  private AirbyteMessageVersionedMigrator<T> migrator;
  private Version protocolVersion;

  private boolean shouldDetectVersion = false;

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
    Preconditions.checkNotNull(protocolVersion);
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.initializeForProtocolVersion(protocolVersion);
  }

  /**
   * Create the AirbyteMessage stream.
   *
   * If detectVersion is set to true, it will decide which protocol version to use from the content of
   * the stream rather than the one passed from the constructor.
   */
  @Trace(operationName = WORKER_OPERATION_NAME)
  @SneakyThrows
  @Override
  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    if (shouldDetectVersion) {
      final Optional<Version> versionMaybe = detectVersion(bufferedReader);
      if (versionMaybe.isPresent()) {
        logger.info("Detected Protocol Version {}", versionMaybe.get().serialize());
        initializeForProtocolVersion(versionMaybe.get());
      } else {
        // No version found, use the default as a fallback
        logger.info("Unable to detect Protocol Version, assuming protocol version {}", fallbackVersion.serialize());
        initializeForProtocolVersion(fallbackVersion);
      }
    }

    final boolean needMigration = !protocolVersion.getMajorVersion().equals(migratorFactory.getMostRecentVersion().getMajorVersion());
    logger.info(
        "Reading messages from protocol version {}{}",
        protocolVersion.serialize(),
        needMigration ? ", messages will be upgraded to protocol version " + migratorFactory.getMostRecentVersion().serialize() : "");
    return super.create(bufferedReader);
  }

  /**
   * Attempt to detect the version by scanning the stream
   *
   * Using the BufferedReader reset/mark feature to get a look-ahead. We will attempt to find the
   * first SPEC message and decide on a protocol version from this message.
   *
   * @param bufferedReader the stream to read
   * @return The Version if found
   * @throws IOException
   */
  private Optional<Version> detectVersion(final BufferedReader bufferedReader) throws IOException {
    // Buffersize needs to be big enough to containing everything we need for the detection. Otherwise,
    // the reset will fail.
    bufferedReader.mark(BUFFER_READ_AHEAD_LIMIT);
    try {
      // Cap detection to the first 10 messages. When doing the protocol detection, we expect the SPEC
      // message to show up early in the stream. Ideally it should be first message however we do not
      // enforce this constraint currently so connectors may send LOG messages before.
      for (int i = 0; i < MESSAGES_LOOK_AHEAD_FOR_DETECTION; ++i) {
        final String line = bufferedReader.readLine();
        final Optional<JsonNode> jsonOpt = Jsons.tryDeserialize(line);
        if (jsonOpt.isPresent()) {
          final JsonNode json = jsonOpt.get();
          if (isSpecMessage(json)) {
            final JsonNode protocolVersionNode = json.at("/spec/protocol_version");
            bufferedReader.reset();
            return Optional.ofNullable(protocolVersionNode).filter(Predicate.not(JsonNode::isMissingNode)).map(node -> new Version(node.asText()));
          }
        }
      }
      bufferedReader.reset();
      return Optional.empty();
    } catch (final IOException e) {
      logger.warn(
          "Protocol version detection failed, it is likely than the connector sent more than {}B without an complete SPEC message." +
              " A SPEC message that is too long could be the root cause here.",
          BUFFER_READ_AHEAD_LIMIT);
      throw e;
    }
  }

  private boolean isSpecMessage(final JsonNode json) {
    return json.has(TYPE_FIELD_NAME) && "spec".equalsIgnoreCase(json.get(TYPE_FIELD_NAME).asText());
  }

  public boolean setDetectVersion(final boolean detectVersion) {
    return this.shouldDetectVersion = detectVersion;
  }

  public VersionedAirbyteStreamFactory<T> withDetectVersion(final boolean detectVersion) {
    setDetectVersion(detectVersion);
    return this;
  }

  final protected void initializeForProtocolVersion(final Version protocolVersion) {
    this.deserializer = (AirbyteMessageDeserializer<T>) serDeProvider.getDeserializer(protocolVersion).orElseThrow();
    this.migrator = migratorFactory.getVersionedMigrator(protocolVersion);
    this.protocolVersion = protocolVersion;
  }

  @Override
  protected Stream<AirbyteMessage> toAirbyteMessage(final JsonNode json) {
    try {
      final io.airbyte.protocol.models.v0.AirbyteMessage message = migrator.upgrade(deserializer.deserialize(json));
      return Stream.of(convert(message));
    } catch (final RuntimeException e) {
      logger.warn("Failed to upgrade a message from version {}: {}", protocolVersion, Jsons.serialize(json), e);
      return Stream.empty();
    }
  }

  // TODO remove this conversion once we migrated default AirbyteMessage to be from a versioned
  // namespace
  private AirbyteMessage convert(final io.airbyte.protocol.models.v0.AirbyteMessage message) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
  }

}
