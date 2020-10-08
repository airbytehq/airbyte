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
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public abstract class TestDestination {

  private static final String STREAM_NAME = "exchange_rate";
  private static final Schema CATALOG = new Schema().withStreams(Lists.newArrayList(
      new io.airbyte.config.Stream().withName(STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("name").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("date").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("NZD").withDataType(DataType.NUMBER).withSelected(true),
              new Field().withName("HKD").withDataType(DataType.NUMBER).withSelected(true)))));

  private StandardTargetConfig targetConfig;
  private TestDestinationEnv testEnv;

  private Path jobRoot;
  protected Path localRoot;
  private ProcessBuilderFactory pbf;

  /**
   * Name of the docker image that the tests will run against.
   *
   * @return docker image name
   */
  protected abstract String getImageName();

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * each test. Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getConfig();

  /**
   * Configuration specific to the integration. Will be passed to integration where appropriate in
   * tests that test behavior when configuration is invalid. e.g incorrect password. Should be
   * invalid.
   *
   * @return integration-specific configuration
   */
  protected abstract JsonNode getInvalidConfig();

  /**
   * Function that returns all of the records in destination as json at the time this method is
   * invoked. These will be used to check that the data actually written is what should actually be
   * there.
   *
   * @param testEnv - information about the test environment.
   * @return All of the records in the destination at the time this method is invoked.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract List<JsonNode> recordRetriever(TestDestinationEnv testEnv) throws Exception;

  /**
   * Function that performs any setup of external resources required for the test. e.g. instantiate a
   * postgres database. This function will be called before EACH test.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void setup(TestDestinationEnv testEnv) throws Exception;

  /**
   * Function that performs any clean up of external resources required for the test. e.g. delete a
   * postgres database. This function will be called after EACH test.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void tearDown(TestDestinationEnv testEnv) throws Exception;

  @BeforeEach
  void setUpInternal() throws Exception {
    this.targetConfig = new StandardTargetConfig()
        .withDestinationConnectionImplementation(new DestinationConnectionImplementation().withConfiguration(getConfig()))
        .withStandardSync(new StandardSync().withSchema(CATALOG));
    Path workspaceRoot = Files.createTempDirectory("test");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);
    localRoot = Files.createTempDirectory("output");
    testEnv = new TestDestinationEnv(localRoot);

    setup(testEnv);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), localRoot.toString(), "host");
  }

  @AfterEach
  void tearDownInternal() throws Exception {
    tearDown(testEnv);
  }

  /**
   * Verify that when given valid credentials, that check connection returns a success response.
   * Assume that the {@link TestDestination#getConfig()} is valid.
   */
  @Test
  void testCheckConnection() {
    // todo (cgardens)
  }

  /**
   * Verify that when given invalid credentials, that check connection returns a failed response.
   * Assume that the {@link TestDestination#getInvalidConfig()} is invalid.
   */
  @Test
  void testCheckConnectionInvalidCredentials() {
    // todo (cgardens)
  }

  /**
   * Verify that the integration successfully writes records. Tests a wide variety of messages and schemas (aspirationally, anyway).
   */
  @Test
  void testSync() throws Exception {
    final DefaultSingerTarget target = new DefaultSingerTarget(getImageName(), pbf);
    final List<SingerMessage> messages = MoreResources.readResource("messages.txt").lines()
        .map(record -> Jsons.deserialize(record, SingerMessage.class)).collect(Collectors.toList());

    target.start(targetConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> target.accept(message)));
    target.notifyEndOfStream();
    target.close();

    final List<JsonNode> actual = recordRetriever(testEnv);
    final List<JsonNode> expected = messages.stream()
        .filter(message -> message.getType() == Type.RECORD)
        .map(SingerMessage::getRecord)
        .collect(Collectors.toList());
    assertEquals(expected, actual);
  }

  /**
   * Verify that the integration overwrites the first sync with the second sync.
   */
  @Test
  void testSecondSync() throws Exception {
    // todo (cgardens)
  }

  public static class TestDestinationEnv {

    private final Path localRoot;

    public TestDestinationEnv(Path localRoot) {
      this.localRoot = localRoot;
    }

    public Path getLocalRoot() {
      return localRoot;
    }

  }

}
