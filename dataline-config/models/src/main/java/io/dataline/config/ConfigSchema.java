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

package io.dataline.config;

import com.google.common.io.Resources;
import io.dataline.commons.io.IOs;
import java.io.File;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystem;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public enum ConfigSchema {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.json"),

  // source
  STANDARD_SOURCE("StandardSource.json"),
  SOURCE_CONNECTION_SPECIFICATION("SourceConnectionSpecification.json"),
  SOURCE_CONNECTION_IMPLEMENTATION("SourceConnectionImplementation.json"),

  // destination
  STANDARD_DESTINATION("StandardDestination.json"),
  DESTINATION_CONNECTION_SPECIFICATION("DestinationConnectionSpecification.json"),
  DESTINATION_CONNECTION_IMPLEMENTATION("DestinationConnectionImplementation.json"),

  // sync
  STANDARD_SYNC("StandardSync.json"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.json"),
  STANDARD_SYNC_SCHEDULE("StandardSyncSchedule.json"),

  STATE("State.json");

  static final Path KNOWN_SCHEMAS_ROOT = prepareSchemas();
  private static final String RESOURCE_DIR = "json";

  /*
   * JsonReferenceProcessor relies on all of the json in consumes being in a file system (not in a
   * jar). This method copies all of the json configs out of the jar into a temporary directory so
   * that JsonReferenceProcessor can find them.
   */
  @SuppressWarnings("UnstableApiUsage")
  private static Path prepareSchemas() {
    try {
      final String rootedResourceDir = String.format("/%s", RESOURCE_DIR);
      final URL url = ConfigSchema.class.getResource(rootedResourceDir);

      Path searchPath;
      if (url.toString().startsWith("jar")) {
        final FileSystem fileSystem = FileSystems.newFileSystem(url.toURI(), Collections.emptyMap());
        searchPath = fileSystem.getPath(rootedResourceDir);
      } else {
        searchPath = Path.of(url.toURI());
      }

      final List<String> filenames = Files.walk(searchPath, 1)
          .map(p -> p.getFileName().toString())
          .filter(p -> p.endsWith(".json"))
          .collect(Collectors.toList());

      final Path configRoot = Files.createTempDirectory("schemas");
      for (String filename : filenames) {
        final URL resource = Resources.getResource(String.format("%s/%s", RESOURCE_DIR, filename));
        IOs.writeFile(configRoot, filename, Resources.toString(resource, StandardCharsets.UTF_8));
      }

      return configRoot;
    } catch (IOException | URISyntaxException e) {
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
