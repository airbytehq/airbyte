package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

public interface StorageId {

  record LocalFileId(String path) implements StorageId {

  }

  record GcsFileId(String bucket, String path) implements StorageId {

  }

  record RabbitMq() implements StorageId {

  }
}
