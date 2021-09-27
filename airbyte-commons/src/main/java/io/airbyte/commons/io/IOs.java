/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import com.google.common.base.Charsets;
import java.io.BufferedReader;
import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.apache.commons.io.input.ReversedLinesFileReader;

public class IOs {

  public static Path writeFile(Path path, String fileName, String contents) {
    final Path filePath = path.resolve(fileName);
    return writeFile(filePath, contents);
  }

  public static Path writeFile(Path filePath, byte[] contents) {
    try {
      Files.write(filePath, contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static Path writeFile(Path filePath, String contents) {
    try {
      Files.writeString(filePath, contents, StandardCharsets.UTF_8);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Writes a file to a random directory in the /tmp folder. Useful as a staging group for test
   * resources.
   */
  public static String writeFileToRandomTmpDir(String filename, String contents) {
    final Path source = Paths.get("/tmp", UUID.randomUUID().toString());
    try {
      Path tmpFile = source.resolve(filename);
      Files.deleteIfExists(tmpFile);
      Files.createDirectory(source);
      writeFile(tmpFile, contents);
      return tmpFile.toString();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static String readFile(Path path, String fileName) {
    return readFile(path.resolve(fileName));
  }

  public static String readFile(Path fullpath) {
    try {
      return Files.readString(fullpath, StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<String> getTail(int numLines, Path path) throws IOException {
    if (path == null) {
      return Collections.emptyList();
    }

    File file = path.toFile();
    if (!file.exists()) {
      return Collections.emptyList();
    }

    try (ReversedLinesFileReader fileReader = new ReversedLinesFileReader(file, Charsets.UTF_8)) {
      List<String> lines = new ArrayList<>();

      String line;
      while ((line = fileReader.readLine()) != null && lines.size() < numLines) {
        lines.add(line);
      }

      Collections.reverse(lines);

      return lines;
    }
  }

  public static InputStream inputStream(final Path path) {
    try {
      return Files.newInputStream(path);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static void silentClose(final Closeable closeable) {
    try {
      closeable.close();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static BufferedReader newBufferedReader(final InputStream inputStream) {
    return new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
  }

}
