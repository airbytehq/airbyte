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
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.config.Stream;
import io.airbyte.singer.SingerMessage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;

class IntegrationRunnerTest {

  private static final String CONFIG_FILE_NAME = "config.json";
  private static final String SCHEMA_FILE_NAME = "schema.json";

  private static final String[] ARGS = new String[] {"args"};

  private static final String CONFIG_STRING = "{ \"username\": \"airbyte\" }";
  private static final JsonNode CONFIG = Jsons.deserialize(CONFIG_STRING);

  private static final Schema SCHEMA = new Schema().withStreams(Lists.newArrayList(new Stream().withName("users")));

  private IntegrationCliParser cliParser;
  private Consumer<String> stdoutConsumer;
  private Destination destination;
  private Path configPath;
  private Path schemaPath;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    cliParser = mock(IntegrationCliParser.class);
    stdoutConsumer = Mockito.mock(Consumer.class);
    destination = mock(Destination.class);
    Path configDir = Files.createTempDirectory("test");

    configPath = IOs.writeFile(configDir, CONFIG_FILE_NAME, CONFIG_STRING);
    schemaPath = IOs.writeFile(configDir, SCHEMA_FILE_NAME, Jsons.serialize(SCHEMA));
  }

  @Test
  void testSpec() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.spec();
    final DestinationConnectionSpecification output = new DestinationConnectionSpecification().withDocumentationUrl("https://docs.airbyte.io/");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.spec()).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination).run(ARGS);

    verify(destination).spec();
    verify(stdoutConsumer).accept(Jsons.serialize(output));
  }

  @Test
  void testCheck() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(configPath.toString());
    final StandardCheckConnectionOutput output = new StandardCheckConnectionOutput().withStatus(Status.FAILURE).withMessage("it failed");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.check(CONFIG)).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination).run(ARGS);

    verify(destination).check(CONFIG);
    verify(stdoutConsumer).accept(Jsons.serialize(output));
  }

  @Test
  void testDiscover() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.discover(configPath.toString());
    final StandardDiscoverSchemaOutput output = new StandardDiscoverSchemaOutput().withSchema(SCHEMA);

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.discover(CONFIG)).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination).run(ARGS);

    verify(destination).discover(CONFIG);
    verify(stdoutConsumer).accept(Jsons.serialize(output));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testWrite() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.write(configPath.toString(), schemaPath.toString());
    final DestinationConsumer<SingerMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.write(CONFIG, SCHEMA)).thenReturn(destinationConsumerMock);

    final IntegrationRunner runner = spy(new IntegrationRunner(cliParser, stdoutConsumer, destination));
    doNothing().when(runner).consumeWriteStream(destinationConsumerMock);
    runner.run(ARGS);

    verify(destination).write(CONFIG, SCHEMA);
    verify(runner).consumeWriteStream(destinationConsumerMock);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testDestinationConsumerLifecycleSuccess() throws Exception {
    final SingerMessage singerMessage1 = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withValue(Jsons.deserialize("{ \"color\": \"blue\" }"));
    final SingerMessage singerMessage2 = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withValue(Jsons.deserialize("{ \"color\": \"yellow\" }"));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(singerMessage1)+ "\n" + Jsons.serialize(singerMessage2)).getBytes()));

    final DestinationConsumer<SingerMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    new IntegrationRunner(null).consumeWriteStream(destinationConsumerMock);

    InOrder inOrder = inOrder(destinationConsumerMock);
    inOrder.verify(destinationConsumerMock).accept(singerMessage1);
    inOrder.verify(destinationConsumerMock).accept(singerMessage2);
    inOrder.verify(destinationConsumerMock).complete();
    inOrder.verify(destinationConsumerMock).close();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testDestinationConsumerLifecycleFailure() throws Exception {
    final SingerMessage singerMessage1 = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withValue(Jsons.deserialize("{ \"color\": \"blue\" }"));
    final SingerMessage singerMessage2 = new SingerMessage()
        .withType(SingerMessage.Type.RECORD)
        .withValue(Jsons.deserialize("{ \"color\": \"yellow\" }"));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(singerMessage1)+ "\n" + Jsons.serialize(singerMessage2)).getBytes()));

    final DestinationConsumer<SingerMessage> destinationConsumerMock = mock(DestinationConsumer.class);
    doThrow(new IOException("error")).when(destinationConsumerMock).accept(singerMessage1);

    assertThrows(IOException.class, () -> new IntegrationRunner(null).consumeWriteStream(destinationConsumerMock));


    InOrder inOrder = inOrder(destinationConsumerMock);
    inOrder.verify(destinationConsumerMock).accept(singerMessage1);
    inOrder.verify(destinationConsumerMock).close();
    inOrder.verifyNoMoreInteractions();
  }

}
