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

package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.rockset.client.RocksetClient;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testng.collections.Sets;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class RocksetDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RocksetDestinationAcceptanceTest.class);
  private static final Set<String> collectionNames = Sets.newHashSet();

  @Override
  protected String getImageName() {
    return "airbyte/destination-rockset:dev";
  }

  @Override
  protected JsonNode getConfig() throws IOException {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    return Jsons.jsonNode(
        ImmutableMap.builder()
            .put("workspace", "commons")
            .put("api_key", "nope nope nope")
            .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(
      TestDestinationEnv testEnv,
      String streamName,
      String namespace,
      JsonNode streamSchema
  ) throws Exception {

    try {
      // As Rockset is not a transactional database, we have to wait a few seconds to be extra sure
      // that we've given documents enough time to be fully indexed when retrieving records
      long sleepTimeSeconds = 30;
      LOGGER.info("Sleeping for {} seconds to wait for records to populate", sleepTimeSeconds);
      Thread.sleep(sleepTimeSeconds * 1000);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
    collectionNames.add(streamName);

    final RocksetClient client = RocksetUtils.clientFromConfig(getConfig());
    String ws = getConfig().get("workspace").asText();
    String sqlText = String.format("SELECT * FROM %s.%s;", ws, streamName);

    return RocksetUtils.query(client, sqlText).stream()
        // remove rockset added fields
        .peek(jn -> ((ObjectNode) jn).remove("_id"))
        .peek(jn -> ((ObjectNode) jn).remove("_event_time"))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws IOException {

  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    JsonNode config = getConfig();
    final RocksetClient client = RocksetUtils.clientFromConfig(config);
    String workspace = config.get("workspace").asText();
    for (String collection : collectionNames) {
      // truncate but don't delete the tables because deletion takes a very long time
      // when running on the free tier there should be no cost
      RocksetUtils.truncateCollection(client, workspace, collection);
    }
  }

}
