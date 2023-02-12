package io.airbyte.integrations.source.e2e_test;


import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.e2e_test.BenchmarkSource.NumRecordsIterator;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class BenchmarkGenerator {

  public static void main(final String[] args) {
//    mainToCSV();
    mainToFile();
  }

  public static void mainToFile() {
    final NumRecordsIterator numRecordsIterator = new NumRecordsIterator(24_000_000);

    final FileWriter fileWriter;
    try {
      fileWriter = new FileWriter("/tmp/benchmark_data.txt");
      final PrintWriter bufferedWriter = new PrintWriter(fileWriter);
      while(numRecordsIterator.hasNext()) {
        bufferedWriter.println(numRecordsIterator.next().getRecord().getData());
      }
      bufferedWriter.flush();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static void mainToCSV() {
    final NumRecordsIterator numRecordsIterator = new NumRecordsIterator(24_000_000);

    final FileWriter fileWriter;
    try {
      fileWriter = new FileWriter("/tmp/benchmark_data2.txt");
      final PrintWriter bufferedWriter = new PrintWriter(fileWriter);
      while(numRecordsIterator.hasNext()) {
        final JsonNode data = numRecordsIterator.next().getRecord().getData();

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
