/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.commons.json.Jsons;
import io.dataline.config.SourceConnectionImplementation;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class SourceImplementationHelpers {

  public static SourceConnectionImplementation generateSourceImplementation(UUID sourceSpecificationId)
      throws IOException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();

    JsonNode implementationJson = getTestImplementationJson();

    final SourceConnectionImplementation sourceConnectionImplementation =
        new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfigurationJson12345(implementationJson);
    sourceConnectionImplementation.setTombstone(false);

    return sourceConnectionImplementation;
  }

  public static JsonNode getTestImplementationJson() throws IOException {
    final Path path =
        Paths.get("../dataline-server/src/test/resources/json/TestImplementation.json");
    return Jsons.deserialize(Files.readString(path));
  }

  public static SourceImplementationRead getSourceImplementationRead(SourceConnectionImplementation sourceImplementation,
                                                                     UUID sourceId) {
    SourceImplementationRead sourceImplementationRead = new SourceImplementationRead();
    sourceImplementationRead.setSourceId(sourceId);
    sourceImplementationRead.setWorkspaceId(sourceImplementation.getWorkspaceId());
    sourceImplementationRead.setSourceSpecificationId(
        sourceImplementation.getSourceSpecificationId());
    sourceImplementationRead.setSourceImplementationId(
        sourceImplementation.getSourceImplementationId());
    sourceImplementationRead.setConnectionConfiguration12345(
        sourceImplementation.getConfigurationJson12345());

    return sourceImplementationRead;
  }

}
