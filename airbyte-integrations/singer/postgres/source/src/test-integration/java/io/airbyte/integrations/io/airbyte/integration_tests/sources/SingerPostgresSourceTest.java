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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverSchemaInput;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.singer.SingerMessage;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.singer.DefaultSingerTap;
import io.airbyte.workers.protocols.singer.SingerCheckConnectionWorker;
import io.airbyte.workers.protocols.singer.SingerDiscoverSchemaWorker;
import io.airbyte.workers.protocols.singer.SingerMessageTracker;
import io.airbyte.workers.protocols.singer.SingerTap;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.compress.utils.Lists;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("rawtypes")
public class SingerPostgresSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerPostgresSourceTest.class);
  private static final String IMAGE_NAME = "airbyte/integration-singer-postgres-source:dev";
  private static final Path TESTS_PATH = Path.of("/tmp/airbyte_integration_tests");

  private PostgreSQLContainer psqlDb;
  private ProcessBuilderFactory pbf;
  private Path jobRoot;

  @BeforeEach
  public void init() throws IOException {
    psqlDb = new PostgreSQLContainer();
    psqlDb.start();

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("simple_postgres_init.sql"), psqlDb);
    Files.createDirectories(TESTS_PATH);
    Path workspaceRoot = Files.createTempDirectory(TESTS_PATH, "airbyte-integration");
    jobRoot = workspaceRoot.resolve("job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "", "host");
  }

  @AfterEach
  public void cleanUp() {
    psqlDb.stop();
  }

  @Test
  public void testReadFirstTime() throws Exception {
    Schema schema = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), Schema.class);

    // select all streams and all fields
    schema.getStreams().forEach(t -> t.setSelected(true));
    schema.getStreams().forEach(t -> t.getFields().forEach(c -> c.setSelected(true)));

    StandardSync syncConfig = new StandardSync().withSyncMode(StandardSync.SyncMode.FULL_REFRESH).withSchema(schema);
    SourceConnectionImplementation sourceImpl =
        new SourceConnectionImplementation().withConfiguration(Jsons.jsonNode(getDbConfig()));

    StandardTapConfig tapConfig = new StandardTapConfig()
        .withStandardSync(syncConfig)
        .withSourceConnectionImplementation(sourceImpl);

    SingerTap singerTap = new DefaultSingerTap(IMAGE_NAME, pbf, new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));
    singerTap.start(tapConfig, jobRoot);

    List<SingerMessage> actualMessages = Lists.newArrayList();
    SingerMessageTracker singerMessageTracker = new SingerMessageTracker();
    while (!singerTap.isFinished()) {
      Optional<SingerMessage> maybeMessage = singerTap.attemptRead();
      if (maybeMessage.isPresent()) {
        singerMessageTracker.accept(maybeMessage.get());
        actualMessages.add(maybeMessage.get());
      }
    }

    for (SingerMessage singerMessage : actualMessages) {
      LOGGER.info("{}", singerMessage);
    }

    JsonNode expectedMessagesContainer = Jsons.deserialize(MoreResources.readResource("simple_schema_expected_messages.json")).get("messages");
    List<SingerMessage> expectedMessages = StreamSupport.stream(expectedMessagesContainer.spliterator(), false)
        .map(msg -> Jsons.deserialize(Jsons.serialize(msg), SingerMessage.class))
        .collect(Collectors.toList());

    assertMessagesEquivalent(expectedMessages, actualMessages);
  }

  private void assertMessagesEquivalent(Collection<SingerMessage> expected, Collection<SingerMessage> actual) {
    for (SingerMessage expectedMessage : expected) {
      assertTrue(isMessagePartiallyContained(expectedMessage, actual), expectedMessage + " was not found in actual messages: " + actual);
    }
  }

  private static boolean isMessagePartiallyContained(SingerMessage message, Collection<SingerMessage> collection) {
    for (SingerMessage containedMessage : collection) {
      if (!message.getType().equals(containedMessage.getType())) {
        continue;
      }
      // We might not want to check that all fields are the same to pass a test e.g: time_extracted isn't
      // something we want a test to fail over.
      // So we copy those "irrelevant" fields to the message before checking for equality
      message.setTimeExtracted(containedMessage.getTimeExtracted());
      // the value field is used for state messages -- no need to compare the exact state messages
      message.setValue(containedMessage.getValue());
      // additional props are not part of the spec
      containedMessage.getAdditionalProperties().forEach(message::setAdditionalProperty);

      if (message.equals(containedMessage)) {
        return true;
      }
    }
    return false;
  }

  @Test
  public void testDiscover() throws IOException {
    StandardDiscoverSchemaInput inputConfig =
        new StandardDiscoverSchemaInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig()));
    OutputAndStatus<StandardDiscoverSchemaOutput> run = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf).run(inputConfig, jobRoot);

    Schema exepcted = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), Schema.class);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(exepcted, run.getOutput().get().getSchema());
  }

  @Test
  public void testSuccessfulConnectionCheck() {
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig()));
    OutputAndStatus<StandardCheckConnectionOutput> run =
        new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf)).run(inputConfig, jobRoot);

    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, run.getOutput().get().getStatus());
  }

  @Test
  public void testInvalidCredsFailedConnectionCheck() {
    Map<String, Object> dbConfig = getDbConfig();
    dbConfig.put("password", "notarealpassword");
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(dbConfig));
    OutputAndStatus<StandardCheckConnectionOutput> run =
        new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf)).run(inputConfig, jobRoot);

    assertEquals(JobStatus.FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, run.getOutput().get().getStatus());
  }

  private Map<String, Object> getDbConfig() {
    Map<String, Object> confMap = new HashMap<>();
    confMap.put("dbname", psqlDb.getDatabaseName());
    confMap.put("user", psqlDb.getUsername());
    confMap.put("password", psqlDb.getPassword());
    confMap.put("port", psqlDb.getFirstMappedPort());
    confMap.put("host", psqlDb.getHost());
    return confMap;
  }

}
