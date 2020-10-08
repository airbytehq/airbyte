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
import com.google.common.base.Preconditions;
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
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
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

  private final TestDestinationConfig testConfig;
  private final StandardTargetConfig targetConfig;
  private final TestDestinationEnv testEnv;

  private Path jobRoot;
  protected Path destinationRoot;
  private ProcessBuilderFactory pbf;

  public TestDestination(TestDestinationConfig testConfig) {
    this.testConfig = testConfig;
    this.targetConfig = new StandardTargetConfig()
        .withDestinationConnectionImplementation(new DestinationConnectionImplementation().withConfiguration(testConfig.getConfig()))
        .withStandardSync(new StandardSync().withSchema(CATALOG));
    this.testEnv = new TestDestinationEnv(destinationRoot);
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
    final DefaultSingerTarget target = new DefaultSingerTarget(testConfig.getImageName(), pbf);
    final List<SingerMessage> messages = MoreResources.readResource("messages.txt").lines()
        .map(record -> Jsons.deserialize(record, SingerMessage.class)).collect(Collectors.toList());

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntimeVoid(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();

    final List<JsonNode> actual = testConfig.getRecordRetriever().apply(testEnv);
    final List<JsonNode> expected = messages.stream()
        .filter(message -> message.getType() == Type.RECORD)
        .map(SingerMessage::getRecord)
        .collect(Collectors.toList());
    assertEquals(expected, actual);
  }

  public static class TestDestinationEnv {
    private final Path destinationRoot;

    public TestDestinationEnv(Path destinationRoot) {
      this.destinationRoot = destinationRoot;
    }

    public Path getDestinationRoot() {
      return destinationRoot;
    }
  }

  public static class TestDestinationConfig {
    private final String imageName;
    private final JsonNode config;
    private final Function<TestDestinationEnv, List<JsonNode>> recordRetriever;
    private final Consumer<TestDestinationEnv> setup;
    private final Consumer<TestDestinationEnv> tearDown;

    public TestDestinationConfig(
        String imageName,
        JsonNode config,
        Function<TestDestinationEnv, List<JsonNode>> recordRetriever,
        Consumer<TestDestinationEnv> setup,
        Consumer<TestDestinationEnv> tearDown
        ) {
      this.imageName = imageName;
      this.config = config;
      this.setup = setup;
      this.tearDown = tearDown;
      this.recordRetriever = recordRetriever;
    }

    public String getImageName() {
      return imageName;
    }

    public JsonNode getConfig() {
      return config;
    }

    public Function<TestDestinationEnv, List<JsonNode>> getRecordRetriever() {
      return recordRetriever;
    }

    public Optional<Consumer<TestDestinationEnv>> getSetup() {
      return Optional.ofNullable(setup);
    }

    public Optional<Consumer<TestDestinationEnv>> getTearDown() {
      return Optional.ofNullable(tearDown);
    }

    public static class Builder {
      private final String imageName;
      private final JsonNode config;
      private final Function<TestDestinationEnv, List<JsonNode>> recordRetriever;
      private Consumer<TestDestinationEnv> setup;
      private Consumer<TestDestinationEnv> tearDown;

      public Builder(String imageName, JsonNode config, Function<TestDestinationEnv, List<JsonNode>> recordRetriever) {
        this.imageName = imageName;
        this.config = config;
        this.recordRetriever = recordRetriever;
      }

      public Builder(String imageName, JsonNode config, Supplier<List<JsonNode>> recordRetriever) {
        this(imageName, config, (path) -> recordRetriever.get());
      }

      public void setSetup(Consumer<TestDestinationEnv> setup) {
        this.setup = setup;
      }

      public void setTearDown(Consumer<TestDestinationEnv> tearDown) {
        this.tearDown = tearDown;
      }

      public TestDestinationConfig build() {
        Preconditions.checkNotNull(imageName);
        Preconditions.checkNotNull(config);
        Preconditions.checkNotNull(recordRetriever);
        return new TestDestinationConfig(imageName, config, recordRetriever, setup, tearDown);
      }
    }
  }

}
