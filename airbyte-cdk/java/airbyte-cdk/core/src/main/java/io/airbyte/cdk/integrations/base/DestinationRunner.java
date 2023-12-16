package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

public class DestinationRunner extends IntegrationRunner {
  public DestinationRunner(final Destination destination) {
    super(new IntegrationCliParser(), Destination::defaultOutputRecordCollector, destination, null);
  }

  @VisibleForTesting
  DestinationRunner(final IntegrationCliParser cliParser,
      final Consumer<AirbyteMessage> outputRecordCollector,
      final Destination destination) {
    super(cliParser, outputRecordCollector, destination, null);
  }

  @VisibleForTesting
  DestinationRunner(final IntegrationCliParser cliParser,
      final Consumer<AirbyteMessage> outputRecordCollector,
      final Destination destination,
      final JsonSchemaValidator jsonSchemaValidator) {
    super(cliParser, outputRecordCollector, destination, null, jsonSchemaValidator);
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
    validateConfig(integration.spec().getConnectionSpecification(), config, "WRITE");
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
}
