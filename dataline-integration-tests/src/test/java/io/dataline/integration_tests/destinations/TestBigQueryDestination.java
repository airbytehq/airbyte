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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.DatasetInfo;
import io.dataline.commons.json.Jsons;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

class TestBigQueryDestination {
  private static final BigQuery BQ = BigQueryOptions.getDefaultInstance().getService();

  private static String datasetName;
  private static Dataset dataset;

  @BeforeAll
  public static void setUp() {
    datasetName = "dataline_tests_" + RandomStringUtils.randomAlphanumeric(8);
    DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetName).build();
    dataset = BQ.create(datasetInfo);
    System.out.println("BQ Dataset " + datasetName + " created...");
  }

  @AfterAll
  public static void tearDown() {
    DatasetId datasetId = dataset.getDatasetId();

    // allows deletion of a dataset that has contents
    BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

    boolean success = BQ.delete(datasetId, option);
    if (success) {
      System.out.println("BQ Dataset " + datasetName + " deleted...");
    } else {
      System.out.println("BQ Dataset cleanup for " + datasetName + " failed!");
    }
  }

  // todo: check that the written file to copy

  @Test
  public void runTest() throws IOException, InterruptedException {
    String partialConfigString = new String(Files.readAllBytes(Paths.get("config/bigquery.json")));
    JsonNode partialConfig = Jsons.deserialize(partialConfigString);

    Map<String, Object> fullConfig = new HashMap<>();

    fullConfig.put("project_id", partialConfig.get("project_id").textValue());
    fullConfig.put("credentials_json", partialConfig.get("credentials_json").textValue());

    fullConfig.put("dataset_id", datasetName);
    fullConfig.put("validate_records", false);
    fullConfig.put("disable_collection", true);
    fullConfig.put("replication_method", "FULL_TABLE");

    System.out.println("fullConfig = " + fullConfig);

    //    // todo: construct config json here
    //    // todo: create config file and validate that the format is correct and override certain
    // parts for the test?
    //    // todo: create script that builds the image and runs this test (and a script to publish)
    //    // todo: mount and submit config file (which has to be validated and have an example in
    // the script)

    final Path testsPath = Path.of("/tmp/tests");
    Files.createDirectories(testsPath);
    Path workspaceRoot = Files.createTempDirectory(testsPath, "dataline");
    Path jobRoot = Path.of(workspaceRoot.toString(), "test1");
    ProcessBuilderFactory pbf =
        new DockerProcessBuilderFactory(workspaceRoot, workspaceRoot.toString(), "host");

    Files.createDirectories(jobRoot);
    Files.writeString(
        Path.of(jobRoot.toString(), "rendered_bigquery.json"), Jsons.serialize(fullConfig));

    // todo: after all deletion of directory

    Process process =
        pbf.create(
                jobRoot,
                "dataline/integration-singer-bigquery-destination",
                "--config",
                "rendered_bigquery.json")
            .redirectError(ProcessBuilder.Redirect.INHERIT)
            .start();

    OutputStream stdin = process.getOutputStream(); // <- Eh?
    InputStream stdout = process.getInputStream();

    BufferedReader reader = new BufferedReader(new InputStreamReader(stdout));
    BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(stdin));

    writer.write("Sup buddy");
    writer.flush();
    writer.close();

    Scanner scanner = new Scanner(stdout);
    while (!process.waitFor(5, TimeUnit.SECONDS)) {
      if (scanner.hasNextLine()) {
        System.out.println(scanner.nextLine());
      }
    }

    process.destroyForcibly();

    System.out.println("exitValue = " + process.exitValue());

    // todo: should just use raw DockerProcessBuilderFactory to exec this with stdin inputstream
    // without testcontainers

    // todo: don't use testcontainers for this since it can't easily pipe in std in? then we can
    // also mount configs as usual or use the local version?

    // todo: do we need to copy file onto image to use it?

    // todo: how do entrypoints/reusing the script paths work here for testing

    List<String> records = new ArrayList<>();

    for (String record : records) {
      // todo container.execInContainer() using the config file and the records
    }

    //    System.out.println(container.getLogs());

    // todo: assert contents exist in BQ
    // todo:
    // https://github.com/googleapis/java-bigquery/blob/master/samples/snippets/src/main/java/com/example/bigquery/Query.java

    System.out.println("hi");
  }
}
