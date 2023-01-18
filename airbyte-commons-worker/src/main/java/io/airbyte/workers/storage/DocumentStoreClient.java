/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import java.util.Optional;

/**
 * Interface for treating cloud storage like a simple document store.
 */
public interface DocumentStoreClient {

  /**
   * Writes a document with a given id. If a document already exists at this id it will be
   * overwritten.
   *
   * @param id of the document to write
   * @param document to write
   */
  void write(String id, String document);

  /**
   * Reads document with a given id.
   *
   * @param id of the document to read.
   * @return the document
   */
  Optional<String> read(String id);

  /**
   * Deletes the document with provided id.
   *
   * @param id of document to delete
   * @return true if deletes something, otherwise false.
   */
  boolean delete(String id);

}
