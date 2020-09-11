/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.integrations.io.dataline.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.commons.json.Jsons;
import io.dataline.commons.resources.MoreResources;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.State;
import io.dataline.db.PostgreSQLContainerHelper;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.protocol.singer.SingerMessageTracker;
import io.dataline.workers.singer.SingerCheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoverSchemaWorker;
import io.dataline.workers.singer.SingerTapFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class SingerPostgresSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerPostgresSourceTest.class);
  private static final String IMAGE_NAME = "dataline/integration-singer-postgres-source";
  private static final Path TESTS_PATH = Path.of("/tmp/dataline_integration_tests");

  private PostgreSQLContainer psqlDb;
  private ProcessBuilderFactory pbf;
  private Path workspaceRoot;
  private Path jobRoot;

  @BeforeEach
  public void init() throws IOException {
    psqlDb = new PostgreSQLContainer();
    psqlDb.start();

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("simple_postgres_init.sql"), psqlDb);
    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "dataline-integration");
    jobRoot = workspaceRoot.resolve("job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "host");
  }

  @AfterEach
  public void cleanUp() {
    psqlDb.stop();
  }

  @Test
  public void testReadFirstTime() throws IOException, InvalidCredentialsException {
    SingerTapFactory singerTapFactory = new SingerTapFactory(IMAGE_NAME, pbf, new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));

    Schema schema = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), Schema.class);

    // select all tables and all columns
    schema.getTables().forEach(t -> t.setSelected(true));
    schema.getTables().forEach(t -> t.getColumns().forEach(c -> c.setSelected(true)));

    StandardSync syncConfig = new StandardSync().withSyncMode(StandardSync.SyncMode.FULL_REFRESH).withSchema(schema);
    SourceConnectionImplementation sourceImpl =
        new SourceConnectionImplementation().withConfiguration(Jsons.jsonNode(getDbConfig()));

    StandardTapConfig tapConfig = new StandardTapConfig()
        .withStandardSync(syncConfig)
        .withSourceConnectionImplementation(sourceImpl);

    Stream<SingerMessage> singerMessageStream = singerTapFactory.create(tapConfig, jobRoot);

    SingerMessageTracker singerMessageTracker = new SingerMessageTracker();
    List<SingerMessage> actualMessages = singerMessageStream.peek(singerMessageTracker).collect(Collectors.toList());
    for (SingerMessage singerMessage : actualMessages) {
      LOGGER.info("{}", singerMessage);
    }

    JsonNode expectedMessagesContainer = Jsons.deserialize(MoreResources.readResource("simple_schema_expected_messages.json")).get("messages");
    List<SingerMessage> expectedMessages = StreamSupport.stream(expectedMessagesContainer.spliterator(), false)
        .map(msg -> Jsons.deserialize(Jsons.serialize(msg), SingerMessage.class))
        .collect(Collectors.toList());

    assertMessagesEquivalent(expectedMessages, actualMessages);

    // test incremental: insert a few more records then run another sync
//    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("simple_postgres_update.sql"), psqlDb);
//
//    StandardSync incrementalStandardSync = new StandardSync().withSyncMode(StandardSync.SyncMode.APPEND).withSchema(schema).;
//    StandardTapConfig incrementalTapConfig = new StandardTapConfig()
//        .withStandardSync(incrementalStandardSync)
//        .withState(new State().withState(singerMessageTracker.getOutputState().get()))
//        .withSourceConnectionImplementation(sourceImpl);
  }

  @Test
  public void testIncrementalRead() {
    // run an initial read, get the state from it
    // add a few more records to the DB
    // pass the state into a second read and make sure the messages are what we expect
    // TODO 
  }

  private void assertMessagesEquivalent(Collection<SingerMessage> expected, Collection<SingerMessage> actual) {
    for (SingerMessage expectedMessage : expected) {
      assertTrue(isMessageContained(expectedMessage, actual), expectedMessage + " was not found in actual messages: " + actual);
    }

  }

  private static boolean isMessageContained(SingerMessage message, Collection<SingerMessage> collection) {
    for (SingerMessage containedMessage : collection) {
      if (!message.getType().equals(containedMessage.getType())) {
        continue;
      }

      // We might not want to check that all fields are the same to pass a test e.g: time_extracted isn't
      // something we want a test to fail over.
      // So we check for equality of a field only if the provided message has that field set. Only
      // exception is a message type since it's a required field.
      if (!isEqualIfSet(message.getAdditionalProperties(), containedMessage.getAdditionalProperties()) ||
          !isEqualIfSet(message.getBookmarkProperties(), containedMessage.getBookmarkProperties()) ||
          !isEqualIfSet(message.getKeyProperties(), containedMessage.getKeyProperties()) ||
          !isEqualIfSet(message.getRecord(), containedMessage.getRecord()) ||
          !isEqualIfSet(message.getSchema(), containedMessage.getSchema()) ||
          !isEqualIfSet(message.getStream(), containedMessage.getStream()) ||
          !isEqualIfSet(message.getTimeExtracted(), containedMessage.getTimeExtracted()) ||
          !isEqualIfSet(message.getValue(), containedMessage.getValue()) ||
          !isEqualIfSet(message.getVersion(), containedMessage.getVersion())) {
        continue;
      }
      return true;
    }
    return false;
  }

  private static boolean isEqualIfSet(Object thiz, Object that) {
    return thiz == null || thiz.equals(that);
  }

  @Test
  public void testDiscover() throws IOException, InvalidCredentialsException {
    StandardDiscoverSchemaInput inputConfig =
        new StandardDiscoverSchemaInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig()));
    OutputAndStatus<StandardDiscoverSchemaOutput> run = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf).run(inputConfig, jobRoot);

    Schema exepcted = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), Schema.class);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(exepcted, run.getOutput().get());
  }

  @Test
  public void testSuccessfulConnectionCheck() throws InvalidCredentialsException, InvalidCatalogException {
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig()));
    OutputAndStatus<StandardCheckConnectionOutput> run =
        new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf)).run(inputConfig, jobRoot);

    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, run.getOutput().get().getStatus());
  }

  @Test
  public void testInvalidCredsFailedConnectionCheck() throws InvalidCredentialsException, InvalidCatalogException {
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
    confMap.put("filter_dbs", psqlDb.getDatabaseName());
    return confMap;
  }

}
