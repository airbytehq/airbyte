/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;

import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class DorisDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DorisDestinationAcceptanceTest.class);

  private JsonNode configJson;

  private static final Path RELATIVE_PATH = Path.of("integration_test/test");





  @Override
  protected String getImageName() {
    return "airbyte/destination-doris:dev";
  }

  @Override
  protected JsonNode getConfig() {
    // TODO: Generate the configuration JSON file to be used for running the destination during the test
    // configJson can either be static and read from secrets/config.json directly
    // or created in the setup method
    configJson = Jsons.deserialize(IOs.readFile(Paths.get("/airbyte/secrets/config.json")));
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // TODO return an invalid config which, when used to run the connector's check connection operation,
    // should result in a failed connection check
    return null;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
          throws IOException {
    // TODO Implement this method to retrieve records which written to the destination by the connector.
    // Records returned from this method will be compared against records provided to the connector
    // to verify they were written correctly

    final List<Path> allOutputs = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());

    final Optional<Path> streamOutput =
            allOutputs.stream()
                    .filter(path -> {
                      return path.getFileName().toString().endsWith(new StandardNameTransformer().getRawTableName(streamName) + ".csv");
                    })
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
  protected void setup(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any setup actions needed before every test case
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any cleanup actions needed after every test case
  }

}
