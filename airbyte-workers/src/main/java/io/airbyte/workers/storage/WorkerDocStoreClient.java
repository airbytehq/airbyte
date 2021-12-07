package io.airbyte.workers.storage;

public interface WorkerDocStoreClient {
  void write(String id, String document);

  String read(String id);
}
