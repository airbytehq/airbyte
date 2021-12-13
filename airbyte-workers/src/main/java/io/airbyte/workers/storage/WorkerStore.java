/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Optional;
import java.util.UUID;

/**
 * JSON layer over { @link CloudDocumentStore }.
 */
public class WorkerStore {

  private final DocumentStoreClient documentStoreClient;

  public WorkerStore(final DocumentStoreClient documentStoreClient) {
    this.documentStoreClient = documentStoreClient;
  }

  /**
   * Set the document for an id. Overwrites existing document, if present.
   *
   * @param id - id to associate document with
   * @param document - document to persist
   */
  void set(final UUID id, final JsonNode document) {
    documentStoreClient.write(id.toString(), Jsons.serialize(document));
  }

  /**
   * Fetch previously persisted document.
   *
   * @param id - id that the document is associated with
   * @return returns document if present, otherwise empty
   */
  Optional<JsonNode> get(final UUID id) {
    return documentStoreClient.read(id.toString()).map(Jsons::deserialize);
  }

  /**
   * Delete persisted document.
   *
   * @param id - id that the document is associated with
   * @return true if actually deletes something, otherwise false. (e.g. false if document doest not
   *         exist).
   */
  boolean delete(final UUID id) {
    return documentStoreClient.delete(id.toString());
  }

}
