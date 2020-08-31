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

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.DatasetInfo;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.shaded.org.apache.commons.lang.RandomStringUtils;

import java.util.ArrayList;
import java.util.List;

class TestBigQueryDestination {
  private static final BigQuery BQ = BigQueryOptions.getDefaultInstance().getService();

  private static String datasetName;
  private static Dataset dataset;

  @BeforeAll
  public static void setUp() {
    datasetName = "dataline-tests-" +  RandomStringUtils.randomAscii(8);
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

  @Test
  public void runTest() {
    // todo: create script that builds the image and runs this test (and a script to publish)
    // todo: mount and submit config file
    GenericContainer<?> container = new GenericContainer<>("dataline/integration-singer-bigquery-destination");
    container.start();

    List<String> records = new ArrayList<>();

    for (String record : records) {
      // todo container.execInContainer() using the config file and the records
    }

    // todo: assert contents exist in BQ
    // todo: https://github.com/googleapis/java-bigquery/blob/master/samples/snippets/src/main/java/com/example/bigquery/Query.java

    System.out.println("hi");
  }
}
