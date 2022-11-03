/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import io.airbyte.commons.io.IOs;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Document store for when all we have is an FS. This should only be used in the docker-compose
 * case. Leverages the workspace mount as a storage area.
 */
public class DockerComposeDocumentStoreClient implements DocumentStoreClient {

  private static final Path STATE_PATH = Path.of("document_store");
  private final Path workspaceMount;

  public static DockerComposeDocumentStoreClient create(final Path workspaceMount) {
    return new DockerComposeDocumentStoreClient(workspaceMount);
  }

  public DockerComposeDocumentStoreClient(final Path workspaceMount) {
    this.workspaceMount = workspaceMount;
  }

  private Path getRoot() {
    return workspaceMount.resolve(STATE_PATH);
  }

  private Path getPath(final String id) {
    return getRoot().resolve(String.format("%s.yaml", id));
  }

  @Override
  public void write(final String id, final String document) {
    final Path path = getPath(id);
    createDirectoryWithParents(path.getParent());
    IOs.writeFile(path, document);
  }

  private void createDirectoryWithParents(final Path path) {
    try {
      Files.createDirectories(path);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public Optional<String> read(final String id) {
    final Path path = getPath(id);
    if (Files.exists(path)) {
      return Optional.ofNullable(IOs.readFile(path));
    } else {
      return Optional.empty();
    }
  }

  @Override
  public boolean delete(final String id) {
    final Path path = getPath(id);
    try {
      return Files.deleteIfExists(path);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

}
