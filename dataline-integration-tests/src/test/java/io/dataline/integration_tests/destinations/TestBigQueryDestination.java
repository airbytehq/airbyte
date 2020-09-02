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

import static java.util.concurrent.TimeUnit.SECONDS;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import com.google.common.base.Charsets;
import io.dataline.commons.json.Jsons;
import io.dataline.workers.WorkerUtils;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TestBigQueryDestination extends BaseIntegrationTestCase {
  private static final BigQuery BQ = BigQueryOptions.getDefaultInstance().getService();

  private String datasetName;
  private Dataset dataset;
  private Process process;

  @BeforeEach
  public void setUpBigQuery() throws IOException {
    datasetName = "dataline_tests_" + RandomStringUtils.randomAlphanumeric(8);
    DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetName).build();
    dataset = BQ.create(datasetInfo);
    System.out.println("BQ Dataset " + datasetName + " created...");

    writeConfigFileToJobRoot();
    process = startTarget();
  }

  @AfterEach
  public void tearDownBigQuery() {
    WorkerUtils.closeProcess(process);

    // allows deletion of a dataset that has contents
    BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

    boolean success = BQ.delete(dataset.getDatasetId(), option);
    if (success) {
      System.out.println("BQ Dataset " + datasetName + " deleted...");
    } else {
      System.out.println("BQ Dataset cleanup for " + datasetName + " failed!");
    }
  }

  @Test
  public void runTest() throws IOException, InterruptedException {
    writeResourceToStdIn("singer-tap-output.txt", process);

    await()
        .atMost(10, SECONDS)
        .until(
            () -> {
              try {
                getExchangeRateTable();
                return true;
              } catch (Exception e) {
                return false;
              }
            });

    TableResult results = getExchangeRateTable();
    List<FieldValueList> actualList =
        StreamSupport.stream(results.iterateAll().spliterator(), false).collect(toList());

    List<FieldValueList> expectedList =
        Arrays.asList(
            FieldValueList.of(
                Arrays.asList(fieldValue(1598918400.0), fieldValue("0.0"), fieldValue("2.0"))),
            FieldValueList.of(
                Arrays.asList(fieldValue(1598918400.0), fieldValue("1.0"), fieldValue("7.0"))));

    for (int i = 0; i < expectedList.size(); i++) {
      FieldValueList actual = actualList.get(i);
      FieldValueList expected = expectedList.get(i);

      System.out.println("actual = " + actual);
      System.out.println("expected = " + expected);

      // compare all except datetime
      for (int j = 1; j < 3; j++) {
        assertEquals(expected.get(j).getValue(), actual.get(j).getValue());
      }
    }
  }

  private Process startTarget() throws IOException {
    return pbf.create(
            jobRoot,
            "dataline/integration-singer-bigquery-destination",
            "--config",
            "rendered_bigquery.json")
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start();
  }

  private void writeConfigFileToJobRoot() throws IOException {

    String partialConfigString = new String(Files.readAllBytes(Paths.get("config/bigquery.json")));
    JsonNode partialConfig = Jsons.deserialize(partialConfigString);

    Map<String, Object> fullConfig = new HashMap<>();

    fullConfig.put("project_id", partialConfig.get("project_id").textValue());
    fullConfig.put("credentials_json", partialConfig.get("credentials_json").textValue());
    fullConfig.put("dataset_id", datasetName);
    fullConfig.put("disable_collection", true);

    Files.writeString(
        Path.of(jobRoot.toString(), "rendered_bigquery.json"), Jsons.serialize(fullConfig));
  }

  private static FieldValue fieldValue(Object object) {
    return FieldValue.of(FieldValue.Attribute.PRIMITIVE, object);
  }

  private void writeResourceToStdIn(String resourceName, Process process) throws IOException {
    BufferedWriter writer =
        new BufferedWriter(new OutputStreamWriter(process.getOutputStream(), Charsets.UTF_8));

    String text =
        new String(getClass().getClassLoader().getResourceAsStream(resourceName).readAllBytes());

    writer.write(text);
    writer.flush();
  }

  private TableResult getExchangeRateTable() throws InterruptedException {
    QueryJobConfiguration queryConfig =
        QueryJobConfiguration.newBuilder("SELECT * FROM " + datasetName + ".exchange_rate;")
            .build();

    return BQ.query(queryConfig);
  }
}
