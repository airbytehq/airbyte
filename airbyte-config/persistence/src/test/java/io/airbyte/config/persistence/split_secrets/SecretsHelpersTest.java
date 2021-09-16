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

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

class SecretsHelpersTest {

  @Test
  void testSplit() throws IOException {
    // prepare an ordered list of uuids to make testing with static config files possible
    final var uuids = List.of(
        UUID.fromString("9eba44d8-51e7-48f1-bde2-619af0e42c22"),
        UUID.fromString("2c2ef2b3-259a-4e73-96d1-f56dacee2e5e")
    // UUID.fromString("1206db5b-b968-4df1-9a76-f3fcdae7e307"),
    // UUID.fromString("c03ef566-79a7-4e77-b6f3-d23d2528f25a"),
    // UUID.fromString("35f08b15-bfd9-44fe-a8c7-5aa9e156c0f5"),
    // UUID.fromString("159c0b6f-f9ae-48b4-b7f3-bcac4ba15743"),
    // UUID.fromString( "71af9b74-4e61-4cff-830e-3bf1ec18fbc0"),
    // UUID.fromString("067a62fc-d007-44dd-a8f6-0fd10823713d"),
    // UUID.fromString("c4967ac9-0856-4733-a21e-1d51ca8f254d")
    );

    final var uuidIterator = uuids.iterator();

    final var workspaceId = UUID.fromString("e0eb0554-ffe0-4e9c-9dc0-ed7f52023eb2");
    final var fullConfig = Jsons.deserialize(MoreResources.readResource("full_config.json"));
    final var spec = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.deserialize(MoreResources.readResource("spec.json")));

    final var splitConfig = SecretsHelpers.split(uuidIterator::next, workspaceId, fullConfig, spec);
    final var expectedPartialConfig = Jsons.deserialize(MoreResources.readResource("expected_partial_config.json"));
    final var expectedSecretMapping = Map.of(
        "workspace_" + workspaceId + "_secret_" + uuids.get(0), "hunter1",
        "workspace_" + workspaceId + "_secret_" + uuids.get(1), "hunter2");

    assertEquals(expectedPartialConfig, splitConfig.getPartialConfig());
    assertEquals(expectedSecretMapping, splitConfig.getSecretIdToPayload());

    // check that keys for Google Secrets Manger fit the requirements:
    // A secret ID is a string with a maximum length of 255 characters and can contain
    // uppercase and lowercase letters, numerals, and the hyphen (-) and underscore (_) characters.
    // via
    // https://cloud.google.com/secret-manager/docs/reference/rpc/google.cloud.secretmanager.v1#createsecretrequest
    final var gsmKeyCharacterPattern = Pattern.compile("^[a-zA-Z0-9_-]+$");

    // sanity check pattern with a character that isn't allowed
    assertFalse(gsmKeyCharacterPattern.matcher("/").matches());

    // check every key
    splitConfig.getSecretIdToPayload().keySet().forEach(key -> {
      assertTrue(gsmKeyCharacterPattern.matcher(key).matches(), "Invalid character in key: " + key);
      assertTrue(key.length() <= 255, "Key is too long: " + key.length());
    });
  }

  @Test
  void testSplitUpdate() {
    // todo
  }

  @Test
  void testCombine() {
    // todo
  }

}
