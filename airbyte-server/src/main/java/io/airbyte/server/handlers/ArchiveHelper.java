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

package io.airbyte.server.handlers;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.StandardCopyOption;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.zip.GZIPOutputStream;
import org.apache.commons.compress.archivers.ArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ArchiveHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationHandler.class);

  static public void createArchive(final Path tempFolder, final Path archiveFile) throws IOException {
    final TarArchiveOutputStream archive =
        new TarArchiveOutputStream(new GZIPOutputStream(new BufferedOutputStream(new FileOutputStream(archiveFile.toFile()))));
    Files.walkFileTree(tempFolder, new SimpleFileVisitor<>() {

      @Override
      public FileVisitResult visitFile(Path file, BasicFileAttributes attributes) {
        // only copy files, no symbolic links
        if (attributes.isSymbolicLink()) {
          return FileVisitResult.CONTINUE;
        }
        Path targetFile = tempFolder.relativize(file);
        try {
          compressFile(file, targetFile, archive);
        } catch (IOException e) {
          LOGGER.error(String.format("Failed to archive file %s: %s", file, e));
          throw new RuntimeException(e);
        }
        return FileVisitResult.CONTINUE;
      }

      @Override
      public FileVisitResult visitFileFailed(Path file, IOException exc) {
        LOGGER.error(String.format("Failed to include file %s in archive", file));
        return FileVisitResult.CONTINUE;
      }

    });
    archive.close();
  }

  static private void compressFile(final Path file, final Path filename, final TarArchiveOutputStream archive) throws IOException {
    final TarArchiveEntry tarEntry = new TarArchiveEntry(file.toFile(), filename.toString());
    archive.putArchiveEntry(tarEntry);
    Files.copy(file, archive);
    archive.closeArchiveEntry();
  }

  static public void openArchive(final Path tempFolder, final Path archiveFile) throws IOException {
    final TarArchiveInputStream archive =
        new TarArchiveInputStream(new GzipCompressorInputStream(new BufferedInputStream(Files.newInputStream(archiveFile))));
    ArchiveEntry entry;
    while ((entry = archive.getNextEntry()) != null) {
      final Path newPath = zipSlipProtect(entry, tempFolder);
      if (entry.isDirectory()) {
        Files.createDirectories(newPath);
      } else {
        final Path parent = newPath.getParent();
        if (parent != null) {
          if (Files.notExists(parent)) {
            Files.createDirectories(parent);
          }
        }
        Files.copy(archive, newPath, StandardCopyOption.REPLACE_EXISTING);
      }
    }
  }

  private static Path zipSlipProtect(ArchiveEntry entry, Path tempFolder)
      throws IOException {
    final Path targetDirResolved = tempFolder.resolve(entry.getName());
    // make sure normalized file still has tempFolder as its prefix,
    // else throws exception
    final Path normalizePath = targetDirResolved.normalize();
    if (!normalizePath.startsWith(tempFolder)) {
      throw new IOException("Bad entry: " + entry.getName());
    }
    return normalizePath;
  }

}
