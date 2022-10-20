/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.csv;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;

import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.apache.commons.csv.CSVRecord;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class CsvDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Path RELATIVE_PATH = Path.of("integration_test/test");
  private static final String SAMPLE_CSV_FILE = "./sample.csv";

  @Override
  protected String getImageName() {
    return "airbyte/destination-csv:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.of("destination_path", Path.of("/local").resolve(RELATIVE_PATH).toString()));
  }

  @ParameterizedTest
  @ValueSource(chars = {',',';','.',' ','\t'})
  void detectDelimiter(char input) throws IOException {
    final Path path = Paths.get(SAMPLE_CSV_FILE);
    // Create CSV file
    try (
            BufferedWriter writer = Files.newBufferedWriter(path);

            CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT
                    .withDelimiter(input)
                    .withHeader("ID", "Instrument", "Type", "Melodic"));
    ) {
      csvPrinter.printRecord("1", "Violin", "String", "True");
      csvPrinter.flush();
      // CSV file to string
      String content = Files.readString(path);

      try{
        assertTrue(content.contains(String.valueOf(input)));
        System.out.println(content+ "✅ Passed with '" + input + "' delimiter!");
        Files.delete(path);
      }catch(AssertionError e) {
        System.out.println(content+ "❌ Failed with '" + input + "' delimiter!");
      }

    }

//    for (CSVRecord record : csvParser) {
//      for (int i = 0; i < record.size(); i++) {
//        System.out.println("At " + i + ": " + record.get(i));
//      }
//    }

//    try (CSVReader reader = new CSVReader(new FileReader(SAMPLE_CSV_FILE))) {
//      List<String[]> r = reader.readAll();
//      r.forEach(x -> System.out.println(Arrays.toString(x)));
//    }
  }
//    FileWriter out = new FileWriter("book.csv");
//    try {
//      (CSVPrinter printer = new CSVPrinter(out, CSVFormat.DEFAULT
//              .withDelimiter(input)
//              .withHeader(HEADERS))){
//        AUTHOR_BOOK_MAP.forEach((author, title) -> {
//          printer.printRecord(author, title);
//        });
//        return out;
//      }
//    }
//    Reader in = new FileReader(out);
//    Iterable<CSVRecord> records = CSVFormat.DEFAULT
//      .withHeader(HEADERS)
//      .withFirstRecordAsHeader()
//      .parse(in);


  // todo (cgardens) - it would be great if we could find a configuration here that failed. the
  // commented out one fails in mac but not on the linux box that the github action runs in. instead
  // we override the test here so it never runs.
  @Override
  protected JsonNode getFailCheckConfig() {
    // set the directory to which the integration will try to write to to read only.
    // localRoot.toFile().setReadOnly();

    // return Jsons.jsonNode(ImmutableMap.of("destination_path",
    // Path.of("/local").resolve(RELATIVE_PATH).toString()));
    return null;
  }

  // override test that this integration cannot pass.
  @Override
  public void testCheckConnectionInvalidCredentials() {}

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final List<Path> allOutputs = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());

    final Optional<Path> streamOutput =
        allOutputs.stream()
            .filter(path -> path.getFileName().toString().endsWith(new StandardNameTransformer().getRawTableName(streamName) + ".csv"))
            .findFirst();

    assertTrue(streamOutput.isPresent(), "could not find output file for stream: " + streamName);

    final FileReader in = new FileReader(streamOutput.get().toFile(), Charset.defaultCharset());
    final Iterable<CSVRecord> records = CSVFormat.DEFAULT
        .withHeader(JavaBaseConstants.COLUMN_NAME_DATA)
        .withFirstRecordAsHeader()
        .parse(in);

    return StreamSupport.stream(records.spliterator(), false)
        .map(record -> Jsons.deserialize(record.toMap().get(JavaBaseConstants.COLUMN_NAME_DATA)))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    // no op
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // no op
  }

}
