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

package io.airbyte.integrations.destination.postgres;


import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.SSHTunnel;
import io.airbyte.integrations.standardtest.destination.DataArgumentsProvider;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.After;
import org.junit.Before;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.workers.WorkerException;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

/**
 * Tests that we can connect to a postgres destination that's tucked away behind an ssh tunnel.  Presumes a bastion host and postgres database are
 * already set up and configured for this scenario.  Uses a generated hash for schema name (and presumes that the service account user has schema
 * create-delete privs) so that the test can run concurrently without clobbering its other run.
 */
public class PostgresDestinationSSHTunnelKeyAcceptanceTest {

  private static final String UNIQUE_RUN_HASH = UUID.randomUUID().toString().replace('-','x').substring(0,10);
  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

  private TestDestinationEnv testEnv;
  private Path jobRoot;
  protected Path localRoot;
  private ProcessFactory processFactory;

  /**
   * Verify that the worker returns a valid spec.
   */
  @Test
  public void testGetSpec() throws WorkerException {
    ConnectorSpecification spec = new DefaultGetSpecWorker(
        new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory))
        .run(new JobGetSpecConfig().withDockerImage(getImageName()), jobRoot);
    assertNotNull(spec);
  }


  /**
   * Configured to use an ssh tunnel with key authentication.
   */
  protected JsonNode getConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_destination_ssh_tunnel_key_config.json")));
  }

  /**
   * Configured to fail, similar to the standard test suite.
   */
  protected JsonNode getFailCheckConfig() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/postgres_destination_ssh_tunnel_key_config.json")));
    ((ObjectNode) config).put("password", "invalidvalue");
    return config;
  }

  /**
   * Verify that when given valid credentials, that check connection returns a success response. Assume that the getConfig() is valid.
   */
  @Test
  public void testCheckConnection() throws Exception {
    assertEquals(Status.SUCCEEDED, runCheck(getConfig()).getStatus());
  }

  /**
   * Verify that when given invalid credentials, that check connection returns a failed response. Assume that the getFailCheckConfig() is invalid.
   */
  @Test
  public void testCheckConnectionInvalidCredentials() throws Exception {
    assertEquals(Status.FAILED, runCheck(getFailCheckConfig()).getStatus());
  }

  private StandardCheckConnectionOutput runCheck(JsonNode config) throws WorkerException {
    return
        new DefaultCheckConnectionWorker(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT,
            getImageName(), processFactory)).run(new
            StandardCheckConnectionInput().withConnectionConfiguration(config), jobRoot);
  }

  /**
   * Prepares the ability to launch a docker worker process for the connector worker.
   */
  @BeforeEach
  void setUpInternal() throws Exception {
    Files.createDirectories(Path.of("/tmp/airbyte_tests/"));
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp/airbyte_tests/"), "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(Path.of("/tmp/airbyte_tests/"), "output");
    processFactory = new DockerProcessFactory(workspaceRoot, workspaceRoot.toString(), localRoot.toString(), "host");
  }

  @Before
  void setUp() throws Exception {
    createUniqueSchema();
  }

  @After
  void tearDown() throws Exception {
    dropUniqueSchema();
  }

  /**
   * Ideally, creating and dropping the transient schema used for a testing should be accomplished
   * in the connector itself (since it is encapsulating the knowledge of the database internals)
   * but for now that API spec doesn't support that, so we'll do it here.
   * @throws Exception
   */
  void dropUniqueSchema() throws Exception {
    final JsonNode config = getConfig();
    // Let's go clean up the schema we used for this test run, with a hashcode in its name.
    String uniqueRunSchema = config.get("schema").asText() + UNIQUE_RUN_HASH;
    ((ObjectNode) config).put("schema",uniqueRunSchema);

    SSHTunnel tunnel = null;
    try {
      tunnel = SSHTunnel.getInstance(config);
      tunnel.openTunnelIfRequested();

      String jdbcUrl = String.format("jdbc:postgresql://%s:%s/", config.get("host").asText(), config.get("port").asInt());
      Database database = Databases.createPostgresDatabase(config.get("username").asText(),
          config.get("password").asText(), jdbcUrl);
      database.query(ctx -> {
        ctx.fetch(String.format("DROP DATABASE %s;", uniqueRunSchema));
        ctx.fetch(String.format("DROP DATABASE _%s;", uniqueRunSchema));
        return null;
      });
    } finally {
      tunnel.closeTunnel();
    }
  }

  /**
   * Ideally, creating and dropping the transient schema used for a testing should be accomplished
   * in the connector itself (since it is encapsulating the knowledge of the database internals)
   * but for now that API spec doesn't support that, so we'll do it here.
   * @throws Exception
   */
  void createUniqueSchema() throws Exception {
    final JsonNode config = getConfig();
    // Let's go clean up the schema we used for this test run, with a hashcode in its name.
    String uniqueRunSchema = config.get("schema").asText() + UNIQUE_RUN_HASH;
    ((ObjectNode) config).put("schema",uniqueRunSchema);

    SSHTunnel tunnel = null;
    try {
      tunnel = SSHTunnel.getInstance(config);
      tunnel.openTunnelIfRequested();

      String jdbcUrl = String.format("jdbc:postgresql://%s:%s/", config.get("host").asText(), config.get("port").asInt());
      Database database = Databases.createPostgresDatabase(config.get("username").asText(),
          config.get("password").asText(), jdbcUrl);
      database.query(ctx -> {
        ctx.fetch(String.format("CREATE SCHEMA IF NOT EXISTS %s;", uniqueRunSchema));
        return null;
      });
    } finally {
      tunnel.closeTunnel();
    }
  }

  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  /**
   * Verify that the integration successfully writes records.
   * Based on DestinationAcceptanceTest but adapted to support concurrency across a persistent external db.
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSync(String messagesFilename, String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = getConfig();
    ((ObjectNode) config).put("schema",config.get("schema") + UNIQUE_RUN_HASH);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);

    // The retrieveRaw line goes into a section of code that needs to be refactored.  It
    // incorrectly assumes that it can create arbitrary connections to the database from anywhere
    // based on internal assumptions about the jdbc connection configuration, and does not leave
    // room for an ssh tunnel.  It should be passing in connection config instead and allowing top level control.
    // TODO: We should come back and clean that up later - this section is the primary reason
    // I created a separate acceptance test instead of reusing the existing hierarchy.
    // The other reason is the unique has on a run.
    //retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  protected void runSyncAndVerifyStateOutput(JsonNode config,
      List<AirbyteMessage> messages,
      ConfiguredAirbyteCatalog catalog,
      boolean runNormalization)
      throws Exception {
    final List<AirbyteMessage> destinationOutput = runSync(config, messages, catalog, runNormalization);
    final AirbyteMessage expectedStateMessage = MoreLists.reversed(messages)
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("All message sets used for testing should include a state record"));

    final AirbyteMessage actualStateMessage = MoreLists.reversed(destinationOutput)
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .findFirst()
        .orElseGet(() -> {
          fail("Destination failed to output state");
          return null;
        });

    assertEquals(expectedStateMessage, actualStateMessage);
  }

  protected AirbyteDestination getDestination() {
    return new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory));
  }


  private List<AirbyteMessage> runSync(JsonNode config, List<AirbyteMessage> messages, ConfiguredAirbyteCatalog catalog, boolean runNormalization)
      throws Exception {

    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(catalog)
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination destination = getDestination();

    destination.start(destinationConfig, jobRoot);
    messages.forEach(message -> Exceptions.toRuntime(() -> destination.accept(message)));
    destination.notifyEndOfStream();

    List<AirbyteMessage> destinationOutput = new ArrayList<>();
    while (!destination.isFinished()) {
      destination.attemptRead().ifPresent(destinationOutput::add);
    }

    destination.close();

    if (!runNormalization) {
      return destinationOutput;
    }

    final NormalizationRunner runner = NormalizationRunnerFactory.create(
        getImageName(),
        processFactory);
    runner.start();
    final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
    if (!runner.normalize(JOB_ID, JOB_ATTEMPT, normalizationRoot, destinationConfig.getDestinationConnectionConfiguration(),
        destinationConfig.getCatalog(), WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS)) {
      throw new WorkerException("Normalization Failed.");
    }
    runner.close();
    return destinationOutput;
  }


}
