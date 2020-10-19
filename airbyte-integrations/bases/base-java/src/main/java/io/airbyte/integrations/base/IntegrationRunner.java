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
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Scanner;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IntegrationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationRunner.class);

  private final IntegrationCliParser cliParser;
  private final Consumer<String> stdoutConsumer;
  private final Destination destination;

  public IntegrationRunner(Destination destination) {
    this(new IntegrationCliParser(), System.out::println, destination);
  }

  @VisibleForTesting
  IntegrationRunner(IntegrationCliParser cliParser, Consumer<String> stdoutConsumer, Destination destination) {
    this.cliParser = cliParser;
    this.stdoutConsumer = stdoutConsumer;
    this.destination = destination;
  }

  public void run(String[] args) throws Exception {
    LOGGER.info("Running integration: {}", destination.getClass().getName());

    final IntegrationConfig parsed = cliParser.parse(args);

    LOGGER.info("Command: {}", parsed.getCommand());
    LOGGER.info("Integration config: {}", parsed);

    switch (parsed.getCommand()) {
      case SPEC -> stdoutConsumer.accept(Jsons.serialize(new AirbyteMessage().withType(Type.SPEC).withSpec(destination.spec())));
      case CHECK -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        stdoutConsumer.accept(Jsons.serialize(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(destination.check(config))));
      }
      case DISCOVER -> {
        throw new IllegalStateException("Discover is not implemented for destinations");
      }
      case READ ->
        // final JsonNode config = parseConfig(parsed.getConfig());
        // final Schema schema = parseConfig(parsed.getSchema(), Schema.class);
        // final State state = parseConfig(parsed.getState(), State.class);
        throw new RuntimeException("Not implemented");
      case WRITE -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        final AirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), AirbyteCatalog.class);
        final DestinationConsumer<AirbyteMessage> consumer = destination.write(config, catalog);
        consumeWriteStream(consumer);
      }
      default -> throw new IllegalStateException("Unexpected value: " + parsed.getCommand());
    }

    LOGGER.info("Completed integration: {}", destination.getClass().getName());
  }

  void consumeWriteStream(DestinationConsumer<AirbyteMessage> consumer) throws Exception {
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
