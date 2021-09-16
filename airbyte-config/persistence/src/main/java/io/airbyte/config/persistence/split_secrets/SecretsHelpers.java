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

import com.fasterxml.jackson.core.JsonPointer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.Preconditions;
import com.jayway.jsonpath.JsonPath;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.UUID;
import java.util.function.Supplier;

public class SecretsHelpers {

  // todo: double check oauth stuff that's already in place
  // todo: create an in memory singleton map secrets store implementation for testing
  // todo: create a separate persistence for secrets that doesn't have config types, is just string to
  // string and allows configuration for a specific prefix
  // todo: test behavior for optional secrets (like the switching in files for example)
  // todo: test an array of secrets - what if you have an array of oneOf? - harddest case is an array
  // of oneofs?
  // todo: CREATION spec + full config -> coordconfig+secrets
  public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {
    Preconditions.checkArgument(fullConfig instanceof ObjectNode, "Full config must be a JSON object!");

    // todo: get paths for all secrets in the spec
    final var schema = spec.getConnectionSpecification();

    System.out.println("output = " + JsonPath.read(schema.toString(), "$[?(@.airbyte_secret == true)]").toString());
    System.out.println("output = " + JsonPath.read(schema.toString(), "$.*.[?(@.airbyte_secret == true)]").toString());
    JsonNode secretTrees = schema.at(JsonPointer.compile("$[?(@.airbyte_secret == true)]"));
    System.out.println("secretTrees = " + secretTrees);

    final var secretParents = schema.findParents("airbyte_secret"); // todo: use constant

    for (JsonNode secretParent : secretParents) {
      System.out.println("secretParent = " + secretParent);
    }

    // todo: one by one, create coordinates and payloads for each spec
    // todo: construct the partial config

    // todo: should we persist things inside here or outside? -> should be inside and should fill the
    // partial spec with coordinates
    // todo: come up with a better name than partialConfig

    // return new SplitSecretConfig(partialConfig, secretIdToPayload);

    return null;
  }

  // todo: UPDATES old coordconfig+spec+ full config -> coordconfig+secrets
  public static SplitSecretConfig splitUpdate(UUID workspaceId, JsonNode oldPartialConfig, JsonNode newFullConfig, ConnectorSpecification spec) {
    // todo: only update if the underlying secret changed value? test this specifically
    return null;
  }

  // todo: READ coordconfig+secets persistence -> full config
  // todo: we'll want permissioning here at some point
  public static JsonNode combine(JsonNode partialConfig, ConfigPersistence secretsPersistence) {
    return null;
  }

  // todo: figure out oauth here
  // todo: test edge cases for json path definitino -> maybe can keep as a tree type or something
}
