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

package io.airbyte.integration_tests.destinations;

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertLinesMatch;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.json.Jsons;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class TestBigQueryDestination {

  private static final BigQuery BQ = BigQueryOptions.getDefaultInstance().getService();
  private static final Logger LOGGER = LoggerFactory.getLogger(TestBigQueryDestination.class);

  private static final Path TESTS_PATH = Path.of("/tmp/airbyte_integration_tests");
  private static final String IMAGE_NAME = "airbyte/integration-singer-bigquery-destination:dev";

  protected Path jobRoot;
  protected Path workspaceRoot;
  protected ProcessBuilderFactory pbf;

  private String datasetName;
  private Dataset dataset;
  private Process process;

  private boolean tornDown = true;

  @BeforeEach
  public void setUpBigQuery() throws IOException {

    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "bigquery");
    jobRoot = Path.of(workspaceRoot.toString(), "job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "", "host");

    datasetName = "airbyte_tests_" + RandomStringUtils.randomAlphanumeric(8);
    DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetName).build();
    dataset = BQ.create(datasetInfo);
    LOGGER.info("BQ Dataset " + datasetName + " created...");

    // make sure bq always get taken down
    tornDown = false;
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  if (!tornDown) {
                    tearDownBigQuery();
                  }
                }));

    writeConfigFileToJobRoot();
    process = startTarget();
  }

  @AfterEach
  public void closeAndTearDown() {
    WorkerUtils.closeProcess(process);
    tearDownBigQuery();
  }

  public void tearDownBigQuery() {
    try {
      // allows deletion of a dataset that has contents
      BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

      boolean success = BQ.delete(dataset.getDatasetId(), option);
      if (success) {
        LOGGER.info("BQ Dataset " + datasetName + " deleted...");
      } else {
        LOGGER.info("BQ Dataset cleanup for " + datasetName + " failed!");
      }

      FileUtils.deleteDirectory(new File(workspaceRoot.toUri()));

      tornDown = true;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  public void runTest() throws IOException, InterruptedException {
    List<String> expectedList =
        Arrays.asList(
            "1598659200.0,2.13,0.12,null",
            "1598745600.0,7.15,1.14,null",
            "1598832000.0,7.99,1.99,10.99",
            "1598918400.0,7.15,1.14,10.16");

    writeResourceToStdIn("singer-tap-output.txt", process);
    process.getOutputStream().close();

    process.waitFor();

    List<String> actualList = getExchangeRateTable();
    assertLinesMatch(expectedList, actualList);
  }

  private Process startTarget() throws IOException {
    return pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        "rendered_bigquery.json")
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private void writeConfigFileToJobRoot() throws IOException {
    String credentialsJsonString = new String(Files.readAllBytes(Paths.get("config/credentials.json")));
    JsonNode credentials = Jsons.deserialize(credentialsJsonString);

    Map<String, Object> fullConfig = new HashMap<>();

    fullConfig.put("project_id", credentials.get("project_id").textValue());
    fullConfig.put("dataset_id", datasetName);
    fullConfig.put("credentials_json", credentialsJsonString);
    fullConfig.put("default_target_schema", datasetName);

    Files.writeString(
        Path.of(jobRoot.toString(), "rendered_bigquery.json"), Jsons.serialize(fullConfig));
  }

  private void writeResourceToStdIn(String resourceName, Process process) throws IOException {
    Objects.requireNonNull(getClass().getClassLoader().getResourceAsStream(resourceName))
        .transferTo(process.getOutputStream());
  }

  private List<String> getExchangeRateTable() throws InterruptedException {
    QueryJobConfiguration queryConfig =
        QueryJobConfiguration.newBuilder(
            "SELECT * FROM " + datasetName + ".exchange_rate ORDER BY date ASC;")
            .setUseQueryCache(false)
            .build();

    TableResult results = BQ.query(queryConfig);

    List<String> resultList =
        StreamSupport.stream(results.iterateAll().spliterator(), false)
            .map(
                x -> x.stream()
                    .map(FieldValue::getValue)
                    .map(String::valueOf)
                    .collect(Collectors.joining(",")))
            .collect(toList());

    return resultList;
  }

}
