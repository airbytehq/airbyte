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

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;

class IntegrationRunnerTest {

  private static final String CONFIG_FILE_NAME = "config.json";
  private static final String CATALOG_FILE_NAME = "catalog.json";

  private static final String[] ARGS = new String[] {"args"};

  private static final String CONFIG_STRING = "{ \"username\": \"airbyte\" }";
  private static final JsonNode CONFIG = Jsons.deserialize(CONFIG_STRING);
  private static final String STREAM_NAME = "users";
  private static final Long EMITTED_AT = Instant.now().toEpochMilli();

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(new AirbyteStream().withName(STREAM_NAME)));

  private IntegrationCliParser cliParser;
  private Consumer<String> stdoutConsumer;
  private Destination destination;
  private Path configPath;
  private Path catalogPath;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    cliParser = mock(IntegrationCliParser.class);
    stdoutConsumer = Mockito.mock(Consumer.class);
    destination = mock(Destination.class);
    Path configDir = Files.createTempDirectory("test");

    configPath = IOs.writeFile(configDir, CONFIG_FILE_NAME, CONFIG_STRING);
    catalogPath = IOs.writeFile(configDir, CATALOG_FILE_NAME, Jsons.serialize(CATALOG));
  }

  @Test
  void testSpec() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.spec();
    final ConnectorSpecification output = new ConnectorSpecification().withDocumentationUrl(new URI("https://docs.airbyte.io/"));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.spec()).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination).run(ARGS);

    verify(destination).spec();
    verify(stdoutConsumer).accept(Jsons.serialize(new AirbyteMessage().withType(Type.SPEC).withSpec(output)));
  }

  @Test
  void testCheck() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(Path.of(configPath.toString()));
    final AirbyteConnectionStatus output = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("it failed");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.check(CONFIG)).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination).run(ARGS);

    verify(destination).check(CONFIG);
    verify(stdoutConsumer).accept(Jsons.serialize(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus((output))));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testWrite() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.write(Path.of(configPath.toString()), Path.of(catalogPath.toString()));
    final DestinationConsumer<AirbyteMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.write(CONFIG, CATALOG)).thenReturn(destinationConsumerMock);

    final IntegrationRunner runner = spy(new IntegrationRunner(cliParser, stdoutConsumer, destination));
    doNothing().when(runner).consumeWriteStream(destinationConsumerMock);
    runner.run(ARGS);

    verify(destination).write(CONFIG, CATALOG);
    verify(runner).consumeWriteStream(destinationConsumerMock);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testDestinationConsumerLifecycleSuccess() throws Exception {
    final AirbyteMessage singerMessage1 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    final AirbyteMessage singerMessage2 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(singerMessage1) + "\n" + Jsons.serialize(singerMessage2)).getBytes()));

    final DestinationConsumer<AirbyteMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    new IntegrationRunner(null).consumeWriteStream(destinationConsumerMock);

    InOrder inOrder = inOrder(destinationConsumerMock);
    inOrder.verify(destinationConsumerMock).accept(singerMessage1);
    inOrder.verify(destinationConsumerMock).accept(singerMessage2);
    inOrder.verify(destinationConsumerMock).close();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testDestinationConsumerLifecycleFailure() throws Exception {
    final AirbyteMessage singerMessage1 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    final AirbyteMessage singerMessage2 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(singerMessage1) + "\n" + Jsons.serialize(singerMessage2)).getBytes()));

    final DestinationConsumer<AirbyteMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    doThrow(new IOException("error")).when(destinationConsumerMock).accept(singerMessage1);

    assertThrows(IOException.class, () -> new IntegrationRunner(null).consumeWriteStream(destinationConsumerMock));

    InOrder inOrder = inOrder(destinationConsumerMock);
    inOrder.verify(destinationConsumerMock).accept(singerMessage1);
    inOrder.verify(destinationConsumerMock).close();
    inOrder.verifyNoMoreInteractions();
  }

}
