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

package io.airbyte.commons.resources;

import com.google.common.base.Preconditions;
import com.google.common.io.Resources;
import io.airbyte.commons.io.IOs;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystem;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.stream.Stream;

public class MoreResources {

  @SuppressWarnings("UnstableApiUsage")
  public static String readResource(String name) throws IOException {
    URL resource = Resources.getResource(name);
    return Resources.toString(resource, StandardCharsets.UTF_8);
  }

  /*
   * This class is a bit of a hack. Might have unexpected behavior.
   */
  public static Stream<Path> listResources(Class<?> klass, String name) throws IOException {
    Preconditions.checkNotNull(klass);
    Preconditions.checkNotNull(name);
    Preconditions.checkArgument(!name.isBlank());

    try {
      final String rootedResourceDir = !name.startsWith("/") ? String.format("/%s", name) : name;
      final URL url = klass.getResource(rootedResourceDir);

      Path searchPath;
      if (url.toString().startsWith("jar")) {
        final FileSystem fileSystem = FileSystems.newFileSystem(url.toURI(), Collections.emptyMap());
        searchPath = fileSystem.getPath(rootedResourceDir);
      } else {
        searchPath = Path.of(url.toURI());
      }

      return Files.walk(searchPath, 1);
    } catch (URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }

  @SuppressWarnings("UnstableApiUsage")
  public static void writeResource(String filename, String contents) {
    final Path source = Paths.get(Resources.getResource("").getPath());
    try {
      Files.deleteIfExists(source.resolve(filename));
      Files.createFile(source.resolve(filename));
      IOs.writeFile(Path.of(Resources.getResource(filename).getPath()), contents);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
