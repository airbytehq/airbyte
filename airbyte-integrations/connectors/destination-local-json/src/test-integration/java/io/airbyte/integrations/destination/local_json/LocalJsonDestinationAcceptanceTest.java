/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.local_json;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class LocalJsonDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Path RELATIVE_PATH = Path.of("integration_test/test");

  @Override
  protected String getImageName() {
    return "airbyte/destination-local-json:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.of("destination_path", RELATIVE_PATH.toString()));
  }

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
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final List<Path> allOutputs = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());
    final Optional<Path> streamOutput = allOutputs.stream()
        .filter(path -> path.getFileName().toString().endsWith(new StandardNameTransformer().getRawTableName(streamName) + ".jsonl"))
        .findFirst();

    assertTrue(streamOutput.isPresent(), "could not find output file for stream: " + streamName);

    return Files.readAllLines(streamOutput.get()).stream()
        .map(Jsons::deserialize)
        .map(o -> o.get(JavaBaseConstants.COLUMN_NAME_DATA))
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
