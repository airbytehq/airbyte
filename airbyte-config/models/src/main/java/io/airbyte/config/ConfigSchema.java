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

package io.airbyte.config;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.resources.MoreResources;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

public enum ConfigSchema {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.yaml"),

  // source
  STANDARD_SOURCE("StandardSource.yaml"),
  SOURCE_CONNECTION_IMPLEMENTATION("SourceConnectionImplementation.yaml"),

  // destination
  STANDARD_DESTINATION("StandardDestination.yaml"),
  DESTINATION_CONNECTION_IMPLEMENTATION("DestinationConnectionImplementation.yaml"),

  // specs
  CONNECTOR_SPECIFICATION("ConnectorSpecification.yaml"),

  // sync
  STANDARD_SYNC("StandardSync.yaml"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.yaml"),
  STANDARD_SYNC_SCHEDULE("StandardSyncSchedule.yaml"),

  STATE("State.yaml");

  static final Path KNOWN_SCHEMAS_ROOT = prepareSchemas();
  private static final String RESOURCE_DIR = "types";

  /*
   * JsonReferenceProcessor relies on all of the json in consumes being in a file system (not in a
   * jar). This method copies all of the json configs out of the jar into a temporary directory so
   * that JsonReferenceProcessor can find them.
   */
  @SuppressWarnings("UnstableApiUsage")
  private static Path prepareSchemas() {
    try {
      final List<String> filenames = MoreResources.listResources(ConfigSchema.class, RESOURCE_DIR)
          .map(p -> p.getFileName().toString())
          .filter(p -> p.endsWith(".yaml"))
          .collect(Collectors.toList());

      final Path configRoot = Files.createTempDirectory("schemas");
      for (String filename : filenames) {
        IOs.writeFile(
            configRoot,
            filename,
            MoreResources.readResource(String.format("%s/%s", RESOURCE_DIR, filename)));
      }

      return configRoot;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private final String schemaFilename;

  ConfigSchema(final String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public File getFile() {
    return KNOWN_SCHEMAS_ROOT.resolve(schemaFilename).toFile();
  }

}
