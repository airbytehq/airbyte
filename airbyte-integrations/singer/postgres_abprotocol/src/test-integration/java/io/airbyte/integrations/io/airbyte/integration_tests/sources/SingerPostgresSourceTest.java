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
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
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
  private static final String IMAGE_NAME = "airbyte/postgres-singer-source-abprotocol:dev";
  private static final Path TESTS_PATH = Path.of("/tmp/airbyte_integration_tests");

  private PostgreSQLContainer psqlDb;
  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;

  @BeforeEach
  public void init() throws IOException {
    psqlDb = new PostgreSQLContainer();
    psqlDb.start();

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("init_ascii.sql"), psqlDb);
    Files.createDirectories(TESTS_PATH);
    Path workspaceRoot = Files.createTempDirectory(TESTS_PATH, "airbyte-integration");
    jobRoot = workspaceRoot.resolve("job");
    Files.createDirectories(jobRoot);

    integrationLauncher = new AirbyteIntegrationLauncher(
        IMAGE_NAME,
        new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "", "host"));
  }

  @AfterEach
  public void cleanUp() {
    psqlDb.stop();
  }

  @Test
  public void testFullRefreshStatelessRead() throws Exception {

    Schema schema = Jsons.deserialize(MoreResources.readResource("schema.json"), Schema.class);

    // select all streams and all fields
    schema.getStreams().forEach(s -> s.setSelected(true));
    schema.getStreams().forEach(t -> t.getFields().forEach(c -> c.setSelected(true)));

    StandardSync syncConfig = new StandardSync().withSyncMode(StandardSync.SyncMode.FULL_REFRESH).withSchema(schema);
    SourceConnectionImplementation sourceImpl =
        new SourceConnectionImplementation().withConfiguration(Jsons.jsonNode(getDbConfig(psqlDb)));

    StandardTapConfig tapConfig = new StandardTapConfig()
        .withStandardSync(syncConfig)
        .withSourceConnectionImplementation(sourceImpl);

    DefaultAirbyteSource source = new DefaultAirbyteSource(integrationLauncher);
    source.start(tapConfig, jobRoot);

    List<AirbyteRecordMessage> actualMessages = Lists.newArrayList();
    while (!source.isFinished()) {
      Optional<AirbyteMessage> maybeMessage = source.attemptRead();
      if (maybeMessage.isPresent() && maybeMessage.get().getType() == AirbyteMessage.Type.RECORD) {
        actualMessages.add(maybeMessage.get().getRecord());
      }
    }

    String lineSeparatedMessages = MoreResources.readResource("expected_messages.txt");
    List<AirbyteRecordMessage> expectedMessages = deserializeLineSeparatedJsons(lineSeparatedMessages, AirbyteRecordMessage.class);

    assertMessagesEquivalent(expectedMessages, actualMessages);
  }

  private void assertMessagesEquivalent(List<AirbyteRecordMessage> expectedMessages, List<AirbyteRecordMessage> actualMessages) {
    assertEquals(expectedMessages.size(), actualMessages.size());

    for (int i = 0; i < expectedMessages.size(); i++) {
      AirbyteRecordMessage expected = expectedMessages.get(i);
      AirbyteRecordMessage actual = actualMessages.get(i);
      assertEquals(expected.getStream(), actual.getStream());
      assertEquals(expected.getData(), actual.getData());
    }
  }

  @Test
  public void testCanReadUtf8() throws IOException, InterruptedException, WorkerException {
    // force the db server to start with sql_ascii encoding to verify the tap can read UTF8 even when
    // default settings are in another encoding
    PostgreSQLContainer db = (PostgreSQLContainer) new PostgreSQLContainer().withCommand("postgres -c client_encoding=sql_ascii");
    db.start();
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("init_utf8.sql"), db);

    String configFileName = "config.json";
    String catalogFileName = "selected_catalog.json";
    writeFileToJobRoot(catalogFileName, MoreResources.readResource(catalogFileName));
    writeFileToJobRoot(configFileName, Jsons.serialize(getDbConfig(db)));

    Process tapProcess = integrationLauncher.read(jobRoot, configFileName, catalogFileName).start();
    tapProcess.waitFor();

    DefaultAirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();
    List<AirbyteRecordMessage> actualMessages = streamFactory.create(IOs.newBufferedReader(tapProcess.getInputStream()))
        .filter(message -> message.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());

    String lineSeparatedMessages = MoreResources.readResource("expected_utf8_messages.txt");
    List<AirbyteRecordMessage> expectedMessages = deserializeLineSeparatedJsons(lineSeparatedMessages, AirbyteRecordMessage.class);

    assertMessagesEquivalent(expectedMessages, actualMessages);

    if (tapProcess.exitValue() != 0) {
      fail("Docker container exited with non-zero exit code: " + tapProcess.exitValue());
    }
  }

  private <T> List<T> deserializeLineSeparatedJsons(String lineSeparatedMessages, Class<T> clazz) {
    return new BufferedReader(new StringReader(lineSeparatedMessages))
        .lines()
        .map(l -> Jsons.deserialize(l, clazz))
        .collect(Collectors.toList());
  }

  @Test
  public void testGetSpec() throws WorkerException, IOException, InterruptedException {
    Process process = integrationLauncher.spec(jobRoot).start();
    process.waitFor();
    InputStream expectedSpecInputStream = Objects.requireNonNull(getClass().getClassLoader().getResourceAsStream("spec.json"));
    JsonNode expectedSpec = Jsons.deserialize(new String(expectedSpecInputStream.readAllBytes()));
    JsonNode actualSpec = Jsons.deserialize(new String(process.getInputStream().readAllBytes()));
    assertEquals(expectedSpec, actualSpec);
  }

  @Test
  public void testDiscover() throws IOException {
    StandardDiscoverCatalogInput inputConfig = new StandardDiscoverCatalogInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig(psqlDb)));
    OutputAndStatus<StandardDiscoverCatalogOutput> run = new DefaultDiscoverCatalogWorker(integrationLauncher).run(inputConfig, jobRoot);

    Schema expected = Jsons.deserialize(MoreResources.readResource("schema.json"), Schema.class);
    assertEquals(JobStatus.SUCCEEDED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(expected, run.getOutput().get().getSchema());
  }

  @Test
  public void testSuccessfulConnectionCheck() {
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(getDbConfig(psqlDb)));
    OutputAndStatus<StandardCheckConnectionOutput> run =
        new DefaultCheckConnectionWorker(integrationLauncher).run(inputConfig, jobRoot);

    assertEquals(JobStatus.SUCCEEDED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCEEDED, run.getOutput().get().getStatus());
  }

  @Test
  public void testInvalidCredsFailedConnectionCheck() {
    Map<String, Object> dbConfig = getDbConfig(psqlDb);
    dbConfig.put("password", "notarealpassword");
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(Jsons.jsonNode(dbConfig));
    OutputAndStatus<StandardCheckConnectionOutput> run =
        new DefaultCheckConnectionWorker(integrationLauncher).run(inputConfig, jobRoot);

    assertEquals(JobStatus.SUCCEEDED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILED, run.getOutput().get().getStatus());
  }

  private Map<String, Object> getDbConfig(PostgreSQLContainer containerDb) {
    Map<String, Object> confMap = new HashMap<>();
    confMap.put("dbname", containerDb.getDatabaseName());
    confMap.put("user", containerDb.getUsername());
    confMap.put("password", containerDb.getPassword());
    confMap.put("port", containerDb.getFirstMappedPort());
    confMap.put("host", containerDb.getHost());
    return confMap;
  }

  private void writeFileToJobRoot(String fileName, String contents) throws IOException {
    Files.writeString(jobRoot.resolve(fileName), contents);
  }

}
