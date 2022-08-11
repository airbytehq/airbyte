/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import io.airbyte.commons.lang.Exceptions;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.zip.GZIPOutputStream;
import org.apache.commons.compress.archivers.ArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream;

public class Archives {

  /**
   * Compress a @param sourceFolder into a Gzip Tarball @param archiveFile
   */
  public static void createArchive(final Path sourceFolder, final Path archiveFile) throws IOException {
    final TarArchiveOutputStream archive =
        new TarArchiveOutputStream(new GZIPOutputStream(new BufferedOutputStream(new FileOutputStream(archiveFile.toFile()))));
    Files.walk(sourceFolder)
        .filter(Files::isRegularFile)
        .forEach(file -> {
          final Path targetFile = sourceFolder.relativize(file);
          Exceptions.toRuntime(() -> compressFile(file, targetFile, archive));
        });
    archive.close();
  }

  private static void compressFile(final Path file, final Path filename, final TarArchiveOutputStream archive) throws IOException {
    final TarArchiveEntry tarEntry = new TarArchiveEntry(file.toFile(), filename.toString());
    archive.putArchiveEntry(tarEntry);
    Files.copy(file, archive);
    archive.closeArchiveEntry();
  }

  /**
   * Uncompress a Gzip Tarball @param archiveFile into the @param destinationFolder
   */
  public static void extractArchive(final Path archiveFile, final Path destinationFolder) throws IOException {
    final TarArchiveInputStream archive =
        new TarArchiveInputStream(new GzipCompressorInputStream(new BufferedInputStream(Files.newInputStream(archiveFile))));
    ArchiveEntry entry = archive.getNextEntry();
    while (entry != null) {
      final Path newPath = zipSlipProtect(entry, destinationFolder);
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
      entry = archive.getNextEntry();
    }
  }

  private static Path zipSlipProtect(final ArchiveEntry entry, final Path destinationFolder)
      throws IOException {
    final Path targetDirResolved = destinationFolder.resolve(entry.getName());
    // make sure normalized file still has destinationFolder as its prefix,
    // else throws exception, see: https://snyk.io/research/zip-slip-vulnerability
    final Path normalizePath = targetDirResolved.normalize();
    if (!normalizePath.startsWith(destinationFolder)) {
      throw new IOException("Bad entry: " + entry.getName());
    }
    return normalizePath;
  }

}
