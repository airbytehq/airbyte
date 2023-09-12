package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

public interface StorageLocation {

  record LocalFileLocation(String path) implements StorageLocation {

  }

  record GcsFileLocation(String bucket, String path) implements StorageLocation {

  }

  record RabbitMq() implements StorageLocation {

  }
}
