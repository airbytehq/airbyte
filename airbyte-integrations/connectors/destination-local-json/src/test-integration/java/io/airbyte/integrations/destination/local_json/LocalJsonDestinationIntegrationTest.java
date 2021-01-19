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

package io.airbyte.integrations.destination.local_json;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class LocalJsonDestinationIntegrationTest extends TestDestination {

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
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName) throws Exception {
    final List<Path> allOutputs = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());
    final Optional<Path> streamOutput = allOutputs.stream()
        .filter(path -> path.getFileName().toString().contains(new StandardNameTransformer().getRawTableName(streamName)))
        .findFirst();

    assertTrue(streamOutput.isPresent(), "could not find output file for stream: " + streamName);

    return Files.readAllLines(streamOutput.get()).stream()
        .map(Jsons::deserialize)
        .map(o -> o.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // no op
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // no op
  }

}
