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

package io.airbyte.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.DestinationImplementationRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.StandardDestination;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class DestinationImplementationHelpers {

  public static JsonNode getTestImplementationJson() throws IOException {
    final Path path =
        Paths.get("../airbyte-server/src/test/resources/json/TestImplementation.json");

    return Jsons.deserialize(Files.readString(path));
  }

  public static DestinationConnectionImplementation generateDestinationImplementation(UUID destinationId)
      throws IOException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID destinationImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    return new DestinationConnectionImplementation()
        .withName("my db2 instance")
        .withWorkspaceId(workspaceId)
        .withDestinationId(destinationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withConfiguration(implementationJson)
        .withTombstone(false);
  }

  public static DestinationImplementationRead getDestinationImplementationRead(DestinationConnectionImplementation destinationImplementation,
                                                                               StandardDestination standardDestination) {

    return new DestinationImplementationRead()
        .destinationId(standardDestination.getDestinationId())
        .workspaceId(destinationImplementation.getWorkspaceId())
        .destinationId(destinationImplementation.getDestinationId())
        .destinationImplementationId(destinationImplementation.getDestinationImplementationId())
        .connectionConfiguration(destinationImplementation.getConfiguration())
        .name(destinationImplementation.getName())
        .destinationName(standardDestination.getName());
  }

}
