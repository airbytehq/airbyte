/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

public class DestinationRunner extends IntegrationRunner<JsonNode> {

  private final Destination destination;

  public DestinationRunner(final Destination destination) {
    super(new IntegrationCliParser(), Destination::defaultOutputRecordCollector);
    this.destination = destination;
  }

  @VisibleForTesting
  DestinationRunner(final IntegrationCliParser cliParser,
                    final Consumer<AirbyteMessage> outputRecordCollector,
                    final Destination destination) {
    super(cliParser, outputRecordCollector);
    this.destination = destination;
  }

  @VisibleForTesting
  DestinationRunner(final IntegrationCliParser cliParser,
                    final Consumer<AirbyteMessage> outputRecordCollector,
                    final Destination destination,
                    final JsonSchemaValidator jsonSchemaValidator) {
    super(cliParser, outputRecordCollector, jsonSchemaValidator);
    this.destination = destination;
  }

  @Override
  protected Integration getIntegration() {
    return destination;
  }

  @Override
  protected void check(IntegrationConfig parsed) throws Exception {
    final JsonNode config = parseConfig(parsed.getConfigPath());
    DestinationConfig.initialize(config);
    check(config);
  }

  @Override
  protected void discover(IntegrationConfig parsed) throws Exception {
    throw new IllegalStateException("Cannot execute discover on a destination!");
  }

  protected void read(IntegrationConfig parsed) throws Exception {
    throw new IllegalStateException("Cannot execute read on a destination!");
  }

  @Override
  protected void write(final IntegrationConfig parsed) throws Exception {
    final JsonNode config = parseConfig(parsed.getConfigPath());
    validateConfig(destination.spec().getConnectionSpecification(), config, "WRITE");
    // save config to singleton
    DestinationConfig.initialize(config);
    final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);

    try (final SerializedAirbyteMessageConsumer consumer = destination.getSerializedMessageConsumer(config, catalog, outputRecordCollector)) {
      consumeWriteStream(consumer);
    } finally {
      stopOrphanedThreads(EXIT_HOOK,
          INTERRUPT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES,
          EXIT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES);
    }
  }

  @Override
  protected Set<String> runValidator(final JsonNode schemaJson, final JsonNode objectJson) {
    return validator.validate(schemaJson, objectJson);
  }

}
