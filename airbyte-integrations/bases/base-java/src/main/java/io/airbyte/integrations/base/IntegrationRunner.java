/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Scanner;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Accepts EITHER a destination or a source. Routes commands from the commandline to the appropriate
 * methods on the integration. Keeps itself DRY for methods that are common between source and
 * destination.
 */
public class IntegrationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationRunner.class);

  private final IntegrationCliParser cliParser;
  private final Consumer<String> stdoutConsumer;
  private final Integration integration;
  private final Destination destination;
  private final Source source;

  public IntegrationRunner(Destination destination) {
    this(new IntegrationCliParser(), System.out::println, destination, null);
  }

  public IntegrationRunner(Source source) {
    this(new IntegrationCliParser(), System.out::println, null, source);
  }

  @VisibleForTesting
  IntegrationRunner(IntegrationCliParser cliParser, Consumer<String> stdoutConsumer, Destination destination, Source source) {
    Preconditions.checkState(destination != null ^ source != null, "can only pass in a destination or a source");
    this.cliParser = cliParser;
    this.stdoutConsumer = stdoutConsumer;
    // integration iface covers the commands that are the same for both source and destination.
    this.integration = source != null ? source : destination;
    this.source = source;
    this.destination = destination;
  }

  public void run(String[] args) throws Exception {
    LOGGER.info("Running integration: {}", integration.getClass().getName());

    final IntegrationConfig parsed = cliParser.parse(args);

    LOGGER.info("Command: {}", parsed.getCommand());
    LOGGER.info("Integration config: {}", parsed);

    switch (parsed.getCommand()) {
      // common
      case SPEC -> stdoutConsumer.accept(Jsons.serialize(new AirbyteMessage().withType(Type.SPEC).withSpec(integration.spec())));
      case CHECK -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        stdoutConsumer.accept(Jsons.serialize(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(integration.check(config))));
      }
      // source only
      case DISCOVER -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        stdoutConsumer.accept(Jsons.serialize(new AirbyteMessage().withType(Type.CATALOG).withCatalog(source.discover(config))));
      }
      // todo (cgardens) - it is incongruous that that read and write return airbyte message (the
      // envelope) while the other commands return what goes inside it.
      case READ -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);
        final Optional<JsonNode> stateOptional = parsed.getStatePath().map(IntegrationRunner::parseConfig);
        final Stream<AirbyteMessage> messageStream = source.read(config, catalog, stateOptional.orElse(null));
        messageStream.map(Jsons::serialize).forEach(stdoutConsumer);
        messageStream.close();
      }
      // destination only
      case WRITE -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);
        final DestinationConsumer<AirbyteMessage> consumer = destination.write(config, catalog);
        consumeWriteStream(consumer);
      }
      default -> throw new IllegalStateException("Unexpected value: " + parsed.getCommand());
    }

    LOGGER.info("Completed integration: {}", integration.getClass().getName());
  }

  static void consumeWriteStream(DestinationConsumer<AirbyteMessage> consumer) throws Exception {
    final Scanner input = new Scanner(System.in);
    try (consumer) {
      while (input.hasNextLine()) {
        final String inputString = input.nextLine();
        final Optional<AirbyteMessage> singerMessageOptional = Jsons.tryDeserialize(inputString, AirbyteMessage.class);
        if (singerMessageOptional.isPresent()) {
          consumer.accept(singerMessageOptional.get());
        } else {
          // todo (cgardens) - decide if we want to throw here instead.
          LOGGER.error(inputString);
        }
      }
    }
  }

  private static JsonNode parseConfig(Path path) {
    return Jsons.deserialize(IOs.readFile(path));
  }

  private static <T> T parseConfig(Path path, Class<T> klass) {
    final JsonNode jsonNode = parseConfig(path);
    return Jsons.object(jsonNode, klass);
  }

}
