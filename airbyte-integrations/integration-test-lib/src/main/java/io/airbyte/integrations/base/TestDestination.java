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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.exception.Exceptions;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.singer.DefaultSingerTarget;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TestDestination {

  private static final String STREAM_NAME = "exchange_rate";
  private static final Schema CATALOG = new Schema().withStreams(Lists.newArrayList(
      new io.airbyte.config.Stream().withName(STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("name").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("date").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("NZD").withDataType(DataType.NUMBER).withSelected(true),
              new Field().withName("HKD").withDataType(DataType.NUMBER).withSelected(true)))));

  private final String imageName;
  private final CheckedFunction<Path, List<JsonNode>, Exception> recordRetriever;
  private final StandardTargetConfig targetConfig;

  private Path jobRoot;
  protected Path destinationRoot;
  private ProcessBuilderFactory pbf;

  public TestDestination(String imageName, JsonNode config, CheckedSupplier<List<JsonNode>, Exception> recordRetriever) {
    this(imageName, config, (path) -> recordRetriever.get());
  }

  public TestDestination(String imageName, JsonNode config, CheckedFunction<Path, List<JsonNode>, Exception> recordRetriever) {
    this.imageName = imageName;
    this.recordRetriever = recordRetriever;
    targetConfig = new StandardTargetConfig()
        .withDestinationConnectionImplementation(new DestinationConnectionImplementation().withConfiguration(config))
        .withStandardSync(new StandardSync().withSchema(CATALOG));
  }

  @BeforeEach
  public void setUp() throws IOException {
    Path workspaceRoot = Files.createTempDirectory("test");
    destinationRoot = Files.createTempDirectory("output");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), destinationRoot.toString(), "host");
  }

  @Test
  void testSync() throws Exception {
    final DefaultSingerTarget target = new DefaultSingerTarget(imageName, pbf);
    final List<SingerMessage> messages = MoreResources.readResource("messages.txt").lines()
        .map(record -> Jsons.deserialize(record, SingerMessage.class)).collect(Collectors.toList());

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntimeVoid(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();

    final List<JsonNode> actual = recordRetriever.apply(destinationRoot);
    final List<JsonNode> expected = messages.stream()
        .filter(message -> message.getType() == Type.RECORD)
        .map(SingerMessage::getRecord)
        .collect(Collectors.toList());
    assertEquals(expected, actual);
  }

}
