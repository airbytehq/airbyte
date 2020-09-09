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

package io.dataline.integration_tests.destinations;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;
import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertLinesMatch;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.singer.SingerCheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoverSchemaWorker;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

class TestPostgresDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestPostgresDestination.class);
  private static final String IMAGE_NAME = "dataline/integration-singer-postgres-destination-docker";
  private static final Path TESTS_PATH = Path.of("/tmp/dataline_integration_tests");
  private static final String CONFIG_FILENAME = "config.json";

  protected Path jobRoot;
  protected Path workspaceRoot;
  protected ProcessBuilderFactory pbf;

  private Process process;

  private PostgreSQLContainer<?> PSQL;

  @BeforeEach
  public void setUp() throws IOException {
    PSQL = new PostgreSQLContainer<>();
    PSQL.start();

    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "dataline-integration");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "host");
  }

  @AfterEach
  public void tearDown() {
    WorkerUtils.closeProcess(process);
    PSQL.stop();
  }

  @Test
  public void runTest() throws IOException, InterruptedException, SQLException {
    writeConfigFileToJobRoot(Jsons.serialize(getDbConfig()));
    process = startTarget();

    List<String> expectedList =
        Arrays.asList(
            "('1598659200', '2.12999999999999989', '0.119999999999999996', null)",
            "('1598745600', '7.15000000000000036', '1.1399999999999999', null)",
            "('1598832000', '7.15000000000000036', '1.1399999999999999', '10.1600000000000001')",
            "('1598918400', '7.15000000000000036', '1.1399999999999999', '10.1600000000000001')");

    writeResourceToStdIn("singer-tap-output.txt", process);
    process.getOutputStream().close();

    process.waitFor();

    List<String> actualList = getExchangeRateTable();
    assertLinesMatch(expectedList, actualList);
  }

  @Test
  public void testConnectionSuccessful() throws InvalidCredentialsException, InvalidCatalogException {
    SingerCheckConnectionWorker checkConnectionWorker = new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(getDbConfig());
    OutputAndStatus<StandardCheckConnectionOutput> run = checkConnectionWorker.run(inputConfig, jobRoot);
    assertEquals(SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, run.getOutput().get().getStatus());
  }

  @Test
  public void testConnectionUnsuccessfulInvalidCreds() throws InvalidCredentialsException, InvalidCatalogException {
    SingerCheckConnectionWorker checkConnectionWorker = new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));
    ObjectNode dbConfig = getDbConfig();
    dbConfig.put("postgres_password", "superfakepassword_nowaythisworks");
    StandardCheckConnectionInput inputConfig = new StandardCheckConnectionInput().withConnectionConfiguration(dbConfig);

    OutputAndStatus<StandardCheckConnectionOutput> run = checkConnectionWorker.run(inputConfig, jobRoot);
    assertEquals(FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, run.getOutput().get().getStatus());
  }

  private Process startTarget() throws IOException {
    return pbf.create(jobRoot, IMAGE_NAME, "--config", CONFIG_FILENAME)
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private ObjectNode getDbConfig() {
    Map<String, Object> fullConfig = new HashMap<>();

    fullConfig.put("postgres_host", PSQL.getHost());
    fullConfig.put("postgres_port", PSQL.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT));
    fullConfig.put("postgres_username", PSQL.getUsername());
    fullConfig.put("postgres_password", PSQL.getPassword());
    fullConfig.put("postgres_database", PSQL.getDatabaseName());
    return (ObjectNode) Jsons.jsonNode(fullConfig);
  }

  private void writeConfigFileToJobRoot(String fileContent) throws IOException {
    Files.writeString(Path.of(jobRoot.toString(), "config.json"), fileContent);
  }

  private void writeResourceToStdIn(String resourceName, Process process) throws IOException {
    Objects.requireNonNull(getClass().getClassLoader().getResourceAsStream(resourceName))
        .transferTo(process.getOutputStream());
  }

  private List<String> getExchangeRateTable() throws SQLException {
    BasicDataSource pool =
        DatabaseHelper.getConnectionPool(PSQL.getUsername(), PSQL.getPassword(), PSQL.getJdbcUrl());

    return DatabaseHelper.query(
        pool,
        ctx -> ctx
            .fetch("SELECT (extract(epoch from date), hkd, nzd, usd) FROM public.exchange_rate ORDER BY date ASC;")
            .stream()
            .map(nestedRecords -> ((Record) nestedRecords.get(0)))
            .map(Record::valuesRow)
            .map(Object::toString)
            .collect(toList()));
  }

}
