package io.airbyte.workers.storage;

import com.fasterxml.jackson.databind.JsonNode;

public interface WorkerDocStoreClient {
  void write(String id, String document);

  String read(String id);
}
