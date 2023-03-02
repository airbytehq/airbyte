/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

/**
 * Generate speed benchmark data and dump it into a file. This uses the same generator as the
 * source-e2e-test. The idea is that we want to be able to use the exact same data in
 * source-e2e-test and in other data sources (e.g. postgres, s3) so that we can do performance
 * comparisons.
 */
public class SpeedBenchmarkFileGenerator {

  public static void main(final String[] args) {
    if (args[0] != null && args[0].contains("csv")) {
      generateCsvFile();
    } else {
      generateTextFile();
    }
  }

  private static SpeedBenchmarkGeneratorIterator getGenerator() {
    return new SpeedBenchmarkGeneratorIterator(24_000_000);
  }

  /**
   * Writes a text file with one record per line. Useful for dumping in S3 / GCS / etc.
   */
  public static void generateTextFile() {
    final SpeedBenchmarkGeneratorIterator speedBenchmarkGeneratorIterator = getGenerator();

    final FileWriter fileWriter;
    try {
      fileWriter = new FileWriter("/tmp/benchmark_data_text.txt", StandardCharsets.UTF_8);
      final PrintWriter bufferedWriter = new PrintWriter(fileWriter);
      while (speedBenchmarkGeneratorIterator.hasNext()) {
        bufferedWriter.println(speedBenchmarkGeneratorIterator.next().getRecord().getData());
      }
      bufferedWriter.flush();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Writes a CSV file with the generated data.
   *
   * This is good for writing a file that can be easily uploaded to postgres with file upload.
   *
   * Command to upload: `\copy stream1 from '/tmp/benchmark_data_csv.txt' delimiter ','`
   */
  public static void generateCsvFile() {
    final SpeedBenchmarkGeneratorIterator speedBenchmarkGeneratorIterator = getGenerator();

    final FileWriter fileWriter;
    try {
      fileWriter = new FileWriter("/tmp/benchmark_data_csv.txt", StandardCharsets.UTF_8);
      final PrintWriter bufferedWriter = new PrintWriter(fileWriter);
      while (speedBenchmarkGeneratorIterator.hasNext()) {
        final JsonNode data = speedBenchmarkGeneratorIterator.next().getRecord().getData();

        final String outputString = String.format("%s,%s,%s,%s,%s",
            data.get("field1").asText(),
            data.get("field2").asText(),
            data.get("field3").asText(),
            data.get("field4").asText(),
            data.get("field5").asText());

        bufferedWriter.println(outputString);
      }
      bufferedWriter.flush();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

}
