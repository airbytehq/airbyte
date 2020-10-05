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

package io.airbyte.integrations.javabase;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Schema;
import io.airbyte.singer.SingerMessage;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Scanner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IntegrationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationRunner.class);

  private final Destination destination;

  public IntegrationRunner(Destination destination) {
    this.destination = destination;
  }

  private void run(String[] args) throws Exception {
    final IntegrationConfig parsed = new IntegrationCliParser().parse(args);

    switch (parsed.getCommand()) {
      case SPEC -> System.out.println(Jsons.serialize(destination.spec()));
      case CHECK -> {
        final JsonNode config = parseConfig(parsed.getConfig());
        System.out.println(Jsons.serialize(destination.check(config)));
      }
      case DISCOVER -> {
        final JsonNode config = parseConfig(parsed.getConfig());
        System.out.println(Jsons.serialize(destination.discover(config)));
      }
      case READ ->
        // final JsonNode config = parseConfig(parsed.getConfig());
        // final Schema schema = parseConfig(parsed.getSchema(), Schema.class);
        // final State state = parseConfig(parsed.getState(), State.class);
        throw new RuntimeException("Not implemented");
      case WRITE -> {
        final JsonNode config = parseConfig(parsed.getConfig());
        final Schema schema = parseConfig(parsed.getSchema(), Schema.class);
        final DestinationConsumer<SingerMessage> consumer = destination.write(config, schema);

        final Scanner input = new Scanner(System.in);
        try (consumer) {
          while (input.hasNextLine()) {
            final Optional<SingerMessage> singerMessageOptional = Jsons.tryDeserialize(input.nextLine(), SingerMessage.class);
            if (singerMessageOptional.isPresent()) {
              consumer.accept(singerMessageOptional.get());
            }
          }
          consumer.complete();
        }
      }
      default -> throw new IllegalStateException("Unexpected value: " + parsed.getCommand());
    }
  }

  private static JsonNode parseConfig(String path) {
    return Jsons.deserialize(IOs.readFile(Path.of(path)));
  }

  private static <T> T parseConfig(String path, Class<T> klass) {
    final JsonNode jsonNode = parseConfig(path);
    return Jsons.object(jsonNode, klass);
  }

  public static void main(String[] args) {
    try {

      final String destinationClass = System.getenv().get(JavaBaseConstants.ENV_DESTINATION_CLASS);
      final String destinationJarPath = System.getenv().get(JavaBaseConstants.ENV_DESTINATION_JAR_PATH);

      LOGGER.info("destination class: {}", destinationClass);
      LOGGER.info("destination jar path: {}", destinationJarPath);

      // add the specific destination to the classpath.
      final URLClassLoader urlClassLoader = new URLClassLoader(new URL[] {Path.of(destinationJarPath).toUri().toURL()});
      Class<?> clazz = Class.forName(destinationClass, true, urlClassLoader);
      Destination destination = (Destination) clazz.getConstructor().newInstance();

      new IntegrationRunner(destination).run(args);
    } catch (Exception e) {
      LOGGER.error("Integration Runner Failed", e);
    }
  }

}
